import re
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
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
    # Пароль не хардкодим: без POSTGRES_PASSWORD в .env/ENV приложение
    # упадёт с понятной ошибкой вместо тихого использования секрета из кода.
    postgres_password: str = Field(..., description="POSTGRES_PASSWORD env/.env")
    api_key: str = "test-key"
    # Флаг управления инфраструктурой при старте (см. lifespan в main.py).
    # create_all остаётся как временное решение до перехода на Alembic.
    auto_create_schema: bool = True

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