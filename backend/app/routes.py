from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from . import repository, schemas
from .config import settings
from .database import get_db


def require_api_key(
    x_api_key: Optional[str] = Header(default=None),
) -> None:
    """
    Простая проверка заголовка:

    X-API-Key: test-key

    Позже можно заменить на JWT/OAuth, но для пет-проекта этого достаточно.
    """

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )


router = APIRouter()


@router.get(
    "/health",
    tags=["health"],
)
def health():
    """
    Проверка доступности сервиса.
    Этот эндпоинт без авторизации.
    """

    return {"status": "ok"}


@router.post(
    "/api/expenses",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ExpenseRead,
    tags=["expenses"],
    dependencies=[Depends(require_api_key)],
)
def create_expense(
    payload: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
):
    """
    Создать расход.
    """

    return repository.create_expense(
        db=db,
        payload=payload,
    )


@router.get(
    "/api/expenses",
    response_model=list[schemas.ExpenseRead],
    tags=["expenses"],
    dependencies=[Depends(require_api_key)],
)
def list_expenses(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
):
    """
    Получить список расходов.
    """

    return repository.list_expenses(
        db=db,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/api/expenses/{expense_id}",
    response_model=schemas.ExpenseRead,
    tags=["expenses"],
    dependencies=[Depends(require_api_key)],
)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить расход по id.
    """

    expense = repository.get_expense_by_id(
        db=db,
        expense_id=expense_id,
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


@router.patch(
    "/api/expenses/{expense_id}",
    response_model=schemas.ExpenseRead,
    tags=["expenses"],
    dependencies=[Depends(require_api_key)],
)
def update_expense(
    expense_id: int,
    payload: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
):
    """
    Частично обновить расход.
    """

    expense = repository.update_expense(
        db=db,
        expense_id=expense_id,
        payload=payload,
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


@router.delete(
    "/api/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["expenses"],
    dependencies=[Depends(require_api_key)],
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    """
    Удалить расход по id.
    """

    deleted = repository.delete_expense(
        db=db,
        expense_id=expense_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)