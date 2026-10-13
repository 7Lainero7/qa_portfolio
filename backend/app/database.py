from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


def ensure_postgres_database_exists() -> None:
    """
    Проверяет, существует ли база из settings.postgres_db.
    Если нет — создаёт её.

    Подключаемся к служебной базе 'postgres', потому что
    создавать новую базу нужно не изнутри самой целевой базы.
    """

    engine = create_engine(
        settings.admin_database_url,
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
        future=True,
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db"),
                {"db": settings.postgres_db},
            )

            database_exists = result.scalar() == 1

            if not database_exists:
                safe_db_name = settings.postgres_db.replace('"', '""')
                conn.execute(text(f'CREATE DATABASE "{safe_db_name}"'))
    finally:
        engine.dispose()



engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()