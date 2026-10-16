import os
from pathlib import Path
import pytest
import psycopg
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / "backend" / ".env")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

@pytest.fixture(scope="module")
def db_conn():
    """Фикстура предоставляет соединение с БД для всех тестов качества."""
    conn = psycopg.connect(DB_URL)
    yield conn
    conn.close()