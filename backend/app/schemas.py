from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


MAX_AMOUNT_CENTS = 100_000_000


class ExpenseBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    amount_cents: int = Field(
        ...,
        gt=0,
        le=MAX_AMOUNT_CENTS,
    )

    category: Optional[str] = Field(
        default="other",
        max_length=30,
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("title must not be blank")

        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> str:
        if value is None:
            return "other"

        value = value.strip()

        if not value:
            return "other"

        return value


class ExpenseCreate(ExpenseBase):
    """
    Схема для создания расхода.
    Используется в POST /api/expenses.
    """
    pass


class ExpenseRead(ExpenseBase):
    """
    Схема для чтения расхода.
    Используется в ответах API.
    """

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=50)
    amount_cents: Optional[int] = Field(default=None, gt=0, le=MAX_AMOUNT_CENTS)
    # category допускает None на уровне схемы: явный null в PATCH означает
    # «сбросить категорию к дефолтной other» (нормализуется в валидаторе ниже).
    # Так поведение PATCH совпадает с POST, где пустое значение тоже -> "other".
    category: Optional[str] = Field(default=None, max_length=30)

    @field_validator("title")
    @classmethod
    def validate_update_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None  # Поле не передано, это ок для PATCH
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value

    @field_validator("category")
    @classmethod
    def validate_update_category(cls, value: Optional[str]) -> Optional[str]:
        # None и пустые строки нормализуем к "other" — колонка NOT NULL,
        # поэтому прямой записи null в БД не будет (защита от 500 сохранена),
        # но контракт единый для POST и PATCH (см. docs/known_issues.md).
        if value is None:
            return "other"
        value = value.strip()
        return value if value else "other"