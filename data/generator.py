import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from faker import Faker


BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / "backend" / ".env")

user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "qa_portfolio")

DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
print(f"Подключение к БД: {host}:{port}/{db}")

fake = Faker('ru_RU')
CATEGORIES = ["food", "transport", "entertainment", "utilities", "other"]


def ensure_database_exists() -> None:
    """
    Создаёт целевую базу, если её нет (симметрично backend/app/database.py).

    Без этого шага тесты Data QA падали с OperationalError, если база
    (например, qa_portfolio_data_test в CI) ещё не существовала:
    сервисный контейнер Postgres создаёт только POSTGRES_DB из своих ENV.
    Подключение идёт к служебной базе 'postgres' в режиме AUTOCOMMIT.
    """
    admin_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,))
            if cur.fetchone() is None:
                cur.execute(
                    psycopg.sql.SQL("CREATE DATABASE {}").format(psycopg.sql.Identifier(db))
                )


def run_generator(num_records: int = 100):
    # Пароль маскируем по значению переменной, а не через getenv:
    # старый вариант DB_URL.replace(os.getenv(...), '***') печатал полный URL,
    # если пароль пришёл из ENV, а .env содержал другое значение.
    print(f"Подключение к БД: {DB_URL.replace(password, '***')}")

    ensure_database_exists()

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # 1. Создаём схему
            schema_path = Path(__file__).parent / "schema.sql"
            cur.execute(schema_path.read_text(encoding="utf-8"))

            # 2. Генерируем и вставляем данные в staging
            # Идемпотентность: схема пересоздаётся через DROP+CREATE, но при эволюции
            # схемы без DROP дубликаты копятся и ломают reconcile-тесты — чистим явно.
            cur.execute("TRUNCATE TABLE staging_expenses RESTART IDENTITY CASCADE")
            print(f"Генерация {num_records} записей в staging...")
            records_to_insert = [
                (fake.sentence(nb_words=3)[:-1], fake.random_int(100, 50000), fake.random_element(CATEGORIES))
                for _ in range(num_records)
            ]
            
            # Добавим один заведомо "плохой" кейс для тестов (дубликат категории с той же суммой, чтобы проверить агрегацию)
            records_to_insert.append(("Test Duplicate", 5000, "food"))
            records_to_insert.append(("Test Duplicate", 5000, "food"))

            cur.executemany(
                "INSERT INTO staging_expenses (title, amount_cents, category) VALUES (%s, %s, %s)",
                records_to_insert
            )


            
            # 3. Выполняем "миграцию": агрегируем данные из staging в mart
            print("Выполнение миграции (агрегация в mart)...")
            cur.execute("""
                INSERT INTO mart_expenses_by_category (category, total_amount_cents, expense_count)
                SELECT 
                    category, 
                    SUM(amount_cents) as total_amount_cents, 
                    COUNT(*) as expense_count
                FROM staging_expenses
                GROUP BY category
                ON CONFLICT (category) 
                DO UPDATE SET 
                    total_amount_cents = EXCLUDED.total_amount_cents,
                    expense_count = EXCLUDED.expense_count,
                    updated_at = CURRENT_TIMESTAMP;
            """)
            
            conn.commit()
            print("✅ Данные успешно сгенерированы и мигрированы!")

if __name__ == "__main__":
    run_generator(100)