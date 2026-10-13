from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine, ensure_postgres_database_exists
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Вызывается при старте приложения.

    1. Проверяем, существует ли нужная база.
    2. Если базы нет — создаём её.
    3. Создаём таблицы.
    """

    ensure_postgres_database_exists()
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Expense API",
    version="0.1.0",
    lifespan=lifespan,
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