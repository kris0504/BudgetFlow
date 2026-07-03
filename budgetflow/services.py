from __future__ import annotations

from budgetflow.errors import NotFoundError
from budgetflow.models import Budget, Transaction, TransactionType
from budgetflow.statistics import StatisticsService
from budgetflow.storage import SQLiteStorage


class FinanceManager:

    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def add_category(self, name: str) -> str:
        return self.storage.add_category(name)

    def list_categories(self) -> list[str]:
        return self.storage.list_categories()

    def delete_category(self, name: str) -> None:
        self.storage.delete_category(name)

    def add_transaction(
        self,
        amount: float,
        category: str,
        transaction_type: str | TransactionType,
        description: str = "",
        transaction_date: str | None = None,
    ) -> Transaction:
        transaction = Transaction(
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            description=description,
            transaction_date=transaction_date,
        )
        return self.storage.add_transaction(transaction)

    def add_income(
        self,
        amount: float,
        category: str,
        description: str = "",
        transaction_date: str | None = None,
    ) -> Transaction:
        return self.add_transaction(
            amount, category, TransactionType.INCOME, description, transaction_date
        )

    def add_expense(
        self,
        amount: float,
        category: str,
        description: str = "",
        transaction_date: str | None = None,
    ) -> Transaction:
        return self.add_transaction(
            amount, category, TransactionType.EXPENSE, description, transaction_date
        )

    def update_transaction(
        self,
        transaction_id: int,
        amount: float,
        category: str,
        transaction_type: str | TransactionType,
        description: str = "",
        transaction_date: str | None = None,
    ) -> Transaction:
        transaction = Transaction(
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            description=description,
            transaction_date=transaction_date,
        )
        return self.storage.update_transaction(transaction_id, transaction)

    def delete_transaction(self, transaction_id: int) -> None:
        self.storage.delete_transaction(transaction_id)

    def list_transactions(self) -> list[Transaction]:
        return self.storage.list_transactions()

    def search_transactions(
        self,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[Transaction]:
        return self.storage.search_transactions(category, start_date, end_date)

    def set_budget(self, category: str, month: str, limit: float) -> Budget:
        return self.storage.set_budget(
            Budget(category=category, month=month, limit=limit)
        )

    def budget_status(self, category: str, month: str) -> dict[str, float | bool]:
        budget = self.storage.get_budget(category, month)
        transactions = self.storage.search_transactions(
            category=category,
            start_date=f"{month}-01",
            end_date=f"{month}-31",
        )
        spent = StatisticsService(transactions).total_expenses()
        remaining = round(budget.limit - spent, 2)
        return {
            "limit": budget.limit,
            "spent": spent,
            "remaining": remaining,
            "is_exceeded": spent > budget.limit,
        }

    def all_budget_statuses(self) -> list[dict[str, str | float | bool]]:
        statuses: list[dict[str, str | float | bool]] = []
        for budget in self.storage.list_budgets():
            status = self.budget_status(budget.category, budget.month)
            statuses.append(
                {"category": budget.category, "month": budget.month, **status}
            )
        return statuses

    def statistics(self) -> StatisticsService:
        return StatisticsService(self.storage.list_transactions())
