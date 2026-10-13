import re
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "qa_portfolio"
    postgres_user: str = "postgres"
    postgres_password: str = "qwer"
    api_key: str = "test-key"

    @field_validator("postgres_db")
    @classmethod
    def validate_postgres_db(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(
                "POSTGRES_DB может содержать только буквы, цифры и подчёркивания"
            )
        return value

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def admin_database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database="postgres",
        )


settings = Settings()


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