from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def create_expense(
    db: Session,
    payload: schemas.ExpenseCreate,
) -> models.Expense:
    """
    Создаёт новую запись расхода.
    """

    expense = models.Expense(**payload.model_dump())

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def get_expense_by_id(
    db: Session,
    expense_id: int,
) -> Optional[models.Expense]:
    """
    Возвращает один расход по id.
    Если расхода нет, вернёт None.
    """

    return (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id)
        .first()
    )


def list_expenses(
    db: Session,
    limit: int = 100,
    offset: int = 0,
) -> list[models.Expense]:
    """
    Возвращает список расходов.

    Новые записи отдаём первыми.
    """

    return (
        db.query(models.Expense)
        .order_by(models.Expense.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_expense(
    db: Session,
    expense_id: int,
    payload: schemas.ExpenseUpdate,
) -> Optional[models.Expense]:
    """
    Частично обновляет расход.

    Обновляются только те поля, которые реально пришли в запросе.
    """

    expense = get_expense_by_id(db, expense_id)

    if expense is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense


def delete_expense(
    db: Session,
    expense_id: int,
) -> bool:
    """
    Удаляет расход по id.

    Возвращает:
    - True, если удалили;
    - False, если объекта не было.

    Реализация — один DELETE с проверкой rowcount, а не SELECT + DELETE.
    Это закрывает race condition: при конкурентном удалении тот запрос,
    который реально удалил строку, получит rowcount == 1, остальные — 0.
    """

    deleted_count = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id)
        .delete(synchronize_session=False)
    )
    db.commit()

    return deleted_count == 1
