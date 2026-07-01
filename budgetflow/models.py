from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional

from budgetflow.errors import ValidationError


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

    @classmethod
    def from_string(cls, value: str) -> "TransactionType":
        try:
            return cls(value.lower())
        except ValueError as exc:
            raise ValidationError("Transaction type must be 'income' or 'expense'.") from exc


@dataclass
class Transaction:
    amount: float
    category: str
    transaction_type: TransactionType
    description: str = ""
    transaction_date: date | None = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.amount = self._validate_amount(self.amount)
        self.category = self._validate_category(self.category)
        self.description = self.description.strip()

        if self.transaction_date is None:
            self.transaction_date = date.today()
        elif isinstance(self.transaction_date, str):
            self.transaction_date = self.parse_date(self.transaction_date)

        if not isinstance(self.transaction_type, TransactionType):
            self.transaction_type = TransactionType.from_string(str(self.transaction_type))

    @property
    def signed_amount(self) -> float:
        if self.transaction_type == TransactionType.INCOME:
            return self.amount
        return -self.amount

    @staticmethod
    def _validate_amount(amount: float) -> float:
        try:
            amount_as_float = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Amount must be a number.") from exc

        if amount_as_float <= 0:
            raise ValidationError("Amount must be positive.")
        return round(amount_as_float, 2)

    @staticmethod
    def _validate_category(category: str) -> str:
        if not isinstance(category, str) or not category.strip():
            raise ValidationError("Category cannot be empty.")
        return category.strip()

    @staticmethod
    def parse_date(value: str) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError("Date must be in YYYY-MM-DD format.") from exc

    @classmethod
    def from_row(cls, row: tuple) -> "Transaction":
        transaction_id, amount, category, transaction_type, description, transaction_date = row
        return cls(
            id=transaction_id,
            amount=amount,
            category=category,
            transaction_type=TransactionType.from_string(transaction_type),
            description=description,
            transaction_date=cls.parse_date(transaction_date),
        )

    def to_database_tuple(self) -> tuple:
        assert self.transaction_date is not None
        return (
            self.amount,
            self.category,
            self.transaction_type.value,
            self.description,
            self.transaction_date.isoformat(),
        )


@dataclass
class Budget:
    category: str
    month: str
    limit: float
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.category = Transaction._validate_category(self.category)
        self.limit = Transaction._validate_amount(self.limit)
        self.month = self._validate_month(self.month)

    @staticmethod
    def _validate_month(month: str) -> str:
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError as exc:
            raise ValidationError("Month must be in YYYY-MM format.") from exc
        return month

    @classmethod
    def from_row(cls, row: tuple) -> "Budget":
        budget_id, category, month, limit = row
        return cls(id=budget_id, category=category, month=month, limit=limit)
