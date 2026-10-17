import os
from pathlib import Path
import pytest
import psycopg
from dotenv import load_dotenv
import sys

# Добавляем путь к generator.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generator import run_generator

BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / "backend" / ".env")

# Безопасная сборка URL (защита от None)
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "qa_portfolio")

DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"


def _truncate_data_tables(conn):
    """Чистим ETL-таблицы перед сессией, если они уже существуют."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename IN ('staging_expenses', 'mart_expenses_by_category')
        """)
        tables = [row[0] for row in cur.fetchall()]
        for table in tables:
            # Имена берутся из каталога БД, не из пользовательского ввода —
            # интерполяция здесь безопасна (psycopg не позволяет биндить имена таблиц).
            cur.execute(f"TRUNCATE TABLE {table} CASCADE")
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def prepare_data_qa_environment():
    """
    Автоматически запускает генератор и миграцию перед всеми тестами Data QA.
    Делает тесты полностью идемпотентными и независимыми от ручных действий.

    Дополнительно убеждаемся, что тесты не идут в «продуктовую» базу:
    это защита от ситуации, когда CI или локальный запуск без ENV
    перезаписал бы данные приложения staging/migrационными DROP+CREATE.
    """
    if db == "qa_portfolio":
        pytest.skip(
            "Data QA требует изолированную базу (POSTGRES_DB=qa_portfolio_data_test): "
            "генератор делает DROP TABLE по своей схеме и может уничтожить продуктовые таблицы."
        )

    print("\n🔄 Автозапуск генерации и миграции данных для Data QA тестов...")
    # Предварительная очистка на случай «осиротевших» таблиц от прошлого упавшего запуска
    with psycopg.connect(DB_URL) as cleanup_conn:
        _truncate_data_tables(cleanup_conn)

    run_generator(num_records=50)
    yield

@pytest.fixture(scope="session")
def db_conn():
    """Предоставляет активное соединение с БД для тестов качества."""
    conn = psycopg.connect(DB_URL)
    yield conn
    conn.close()