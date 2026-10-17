from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine, ensure_postgres_database_exists
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Вызывается при старте приложения.

    Инфраструктурные действия (создание БД и таблиц) вынесены под флаг
    AUTO_CREATE_SCHEMA по умолчанию включён для удобства локальной разработки.
    В CI/тестах схема готовится фикстурами, а на «продакшн»-подобных
    окружениях этот путь должен быть отключён в пользу миграций (Alembic).
    """

    if settings.auto_create_schema:
        ensure_postgres_database_exists()
        Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Expense API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )