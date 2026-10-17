import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine, ensure_postgres_database_exists, SessionLocal
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """
    Готовит тестовую базу один раз на всю сессию тестов.
    1. Создаёт базу, если её нет.
    2. Создаёт таблицы.

    Конфигурация (POSTGRES_DB=qa_portfolio_test и т.д.) приходит из ENV —
    см. backend.yml в CI и README для локального запуска. Мутация
    os.environ до импортов приложения больше не нужна: pydantic-settings
    читает ENV при создании Settings(), а ENV из CI/-shell имеет приоритет
    над backend/.env.
    """
    assert settings.postgres_db.endswith("_test"), (
        f"Опасная конфигурация: тесты пойдут в базу '{settings.postgres_db}'. "
        "Ожидается база с суффиксом *_test (POSTGRES_DB=qa_portfolio_test)."
    )
    ensure_postgres_database_exists()
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def clean_expenses():
    """
    Очищает таблицу expenses ПЕРЕД каждым тестом.

    Очистка «до», а не «после», делает тесты устойчивыми к падению
    предыдущего запуска: грязное состояние из прошлого раза гарантированно
    будет удалено перед стартом нового теста.
    """
    session = SessionLocal()
    try:
        session.execute(text("TRUNCATE TABLE expenses RESTART IDENTITY CASCADE"))
        session.commit()
    finally:
        session.close()

    yield


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