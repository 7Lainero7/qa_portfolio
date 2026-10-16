import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ["POSTGRES_DB"] = "qa_portfolio_test"

from app.config import settings
from app.database import Base, engine, ensure_postgres_database_exists, SessionLocal
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """
    Готовит тестовую базу один раз на всю сессию тестов.
    1. Создаёт базу, если её нет.
    2. Создаёт таблицы.
    """
    ensure_postgres_database_exists()
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def clean_expenses():
    """
    Очищает таблицу expenses после каждого теста.
    Так тесты не влияют друг на друга.
    """
    yield

    session = SessionLocal()
    try:
        session.execute(text("TRUNCATE TABLE expenses RESTART IDENTITY CASCADE"))
        session.commit()
    finally:
        session.close()


@pytest.fixture()
def client():
    """
    Клиент для тестирования FastAPI приложения.
    """
    return TestClient(app)


@pytest.fixture()
def auth_headers():
    """
    Заголовок авторизации для защищённых эндпоинтов.
    ВАЖНО: Берем ключ из настроек, а не хардкодим, чтобы тесты не падали при смене API_KEY в .env
    """
    return {"X-API-Key": settings.api_key}


@pytest.fixture()
def payload_factory():
    """
    Фабрика полезных тел запросов.
    """
    def _make(**overrides):
        payload = {
            "title": "Coffee",
            "amount_cents": 35000,
            "category": "food",
        }
        payload.update(overrides)
        return payload

    return _make