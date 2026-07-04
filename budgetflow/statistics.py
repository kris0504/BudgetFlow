from __future__ import annotations

from collections import defaultdict

from budgetflow.models import Transaction, TransactionType


class StatisticsService:
    """Calculates totals and reports from transactions."""

    def __init__(self, transactions: list[Transaction]) -> None:
        self.transactions = transactions

    @staticmethod
    def _is_in_month(transaction: Transaction, month: str | None) -> bool:
        if month is None:
            return True

        assert transaction.transaction_date is not None
        return transaction.transaction_date.strftime("%Y-%m") == month

    def total_income(self) -> float:
        return round(
            sum(
                t.amount
                for t in self.transactions
                if t.transaction_type == TransactionType.INCOME
            ),
            2,
        )

    def total_expenses(self) -> float:
        return round(
            sum(
                t.amount
                for t in self.transactions
                if t.transaction_type == TransactionType.EXPENSE
            ),
            2,
        )

    def balance(self) -> float:
        return round(sum(t.signed_amount for t in self.transactions), 2)

    def expenses_by_category(self, month: str | None = None) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for transaction in self.transactions:
            if (
                transaction.transaction_type == TransactionType.EXPENSE
                and self._is_in_month(transaction, month)
            ):
                totals[transaction.category] += transaction.amount
        return {category: round(amount, 2) for category, amount in totals.items()}

    def income_by_category(self) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for transaction in self.transactions:
            if transaction.transaction_type == TransactionType.INCOME:
                totals[transaction.category] += transaction.amount
        return {category: round(amount, 2) for category, amount in totals.items()}

    def monthly_summary(self) -> dict[str, dict[str, float]]:
        summary: dict[str, dict[str, float]] = defaultdict(
            lambda: {"income": 0.0, "expense": 0.0, "balance": 0.0}
        )
        for transaction in self.transactions:
            assert transaction.transaction_date is not None
            month = transaction.transaction_date.strftime("%Y-%m")
            if transaction.transaction_type == TransactionType.INCOME:
                summary[month]["income"] += transaction.amount
            else:
                summary[month]["expense"] += transaction.amount
            summary[month]["balance"] += transaction.signed_amount

        return {
            month: {key: round(value, 2) for key, value in values.items()}
            for month, values in sorted(summary.items(), reverse=True)
        }

    def monthly_totals(self, month: str) -> dict[str, float]:
        summary = self.monthly_summary()
        return summary.get(month, {"income": 0.0, "expense": 0.0, "balance": 0.0})

    def top_expense_categories(
        self, limit: int = 5, month: str | None = None
    ) -> list[tuple[str, float]]:
        return sorted(
            self.expenses_by_category(month).items(),
            key=lambda item: item[1],
            reverse=True,
        )[:limit]
