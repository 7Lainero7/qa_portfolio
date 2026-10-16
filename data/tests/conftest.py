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

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

@pytest.fixture(scope="session", autouse=True)
def prepare_data_qa_environment():
    """Автоматически запускает генератор и миграцию перед всеми тестами Data QA."""
    print("\n🔄 Запуск генерации и миграции данных для тестов...")
    run_generator(num_records=50) # 50 записей достаточно для тестов
    yield
    # Опционально: очистка после всех тестов