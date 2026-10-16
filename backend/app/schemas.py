from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    amount_cents: int = Field(
        ...,
        gt=0,
        le=100_000_000,
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
    amount_cents: Optional[int] = Field(default=None, gt=0, le=100_000_000)
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
        if value is None:
            raise ValueError("category cannot be null in PATCH request") # ← Блокируем 500 ошибку
        value = value.strip()
        return value if value else "other"