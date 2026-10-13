from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    String,
    func,
)

from .database import Base


class Expense(Base):
    __tablename__ = "expenses"

    __table_args__ = (
        CheckConstraint(
            "amount_cents > 0",
            name="ck_expenses_amount_cents_positive",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(50),
        nullable=False,
    )

    amount_cents = Column(
        BigInteger,
        nullable=False,
    )

    category = Column(
        String(30),
        nullable=False,
        default="other",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )