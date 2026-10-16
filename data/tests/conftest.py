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

@pytest.fixture(scope="session", autouse=True)
def prepare_data_qa_environment():
    """
    Автоматически запускает генератор и миграцию перед всеми тестами Data QA.
    Делает тесты полностью идемпотентными и независимыми от ручных действий.
    """
    print("\n🔄 Автозапуск генерации и миграции данных для Data QA тестов...")
    run_generator(num_records=50)
    yield

@pytest.fixture(scope="session")
def db_conn():
    """Предоставляет активное соединение с БД для тестов качества."""
    conn = psycopg.connect(DB_URL)
    yield conn
    conn.close()