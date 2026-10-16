import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from faker import Faker

# Загружаем переменные из backend/.env (чтобы использовать те же настройки БД)
BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / "backend" / ".env")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

fake = Faker('ru_RU')
CATEGORIES = ["food", "transport", "entertainment", "utilities", "other"]

def run_generator(num_records: int = 100):
    print(f"Подключение к БД: {DB_URL.replace(os.getenv('POSTGRES_PASSWORD'), '***')}")
    
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # 1. Создаём схему
            schema_path = Path(__file__).parent / "schema.sql"
            cur.execute(schema_path.read_text(encoding="utf-8"))
            
            # 2. Генерируем и вставляем данные в staging
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