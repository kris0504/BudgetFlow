from __future__ import annotations

from budgetflow.models import TransactionType
from budgetflow.statistics import StatisticsService


class ReportGenerator:

    def __init__(self, statistics: StatisticsService) -> None:
        self.statistics = statistics

    def monthly_text_report(self, month: str | None = None) -> str:
        if month is not None:
            return self._single_month_report(month)

        monthly_summary = self.statistics.monthly_summary()

        lines = ["BUDGETFLOW MONTHLY REPORT", "=========================", ""]
        for current_month, data in monthly_summary.items():
            lines.append(f"{current_month}")
            lines.append("-" * 32)
            lines.append(f"Income   : {data['income']:.2f} BGN")
            lines.append(f"Expenses : {data['expense']:.2f} BGN")
            lines.append(f"Balance  : {data['balance']:.2f} BGN")
            lines.append("")

        if not monthly_summary:
            lines.append("No transactions yet.")

        return "\n".join(lines)

    def _single_month_report(self, month: str) -> str:
        data = self.statistics.monthly_totals(month)
        expenses = self.statistics.expenses_by_category(month)

        month_transactions = [
            transaction
            for transaction in self.statistics.transactions
            if transaction.transaction_date.strftime("%Y-%m") == month
        ]

        income_transactions = [
            transaction
            for transaction in month_transactions
            if transaction.transaction_type == TransactionType.INCOME
        ]

        expense_transactions = [
            transaction
            for transaction in month_transactions
            if transaction.transaction_type == TransactionType.EXPENSE
        ]

        transaction_count = len(month_transactions)
        income_count = len(income_transactions)
        expense_count = len(expense_transactions)

        average_expense = 0.0
        if expense_transactions:
            average_expense = round(
                sum(transaction.amount for transaction in expense_transactions)
                / len(expense_transactions),
                2,
            )

        if data["income"] > 0:
            savings_rate = round((data["balance"] / data["income"]) * 100, 2)
            savings_rate_text = f"{savings_rate:.2f}%"
        else:
            savings_rate_text = "N/A"

        top_category = None
        if expenses:
            top_category = max(expenses.items(), key=lambda item: item[1])

        lines = [
            f"BUDGETFLOW REPORT — {month}",
            "=" * 42,
            "",
            "OVERVIEW",
            "-" * 42,
            f"Income               : {data['income']:.2f} BGN",
            f"Expenses             : {data['expense']:.2f} BGN",
            f"Balance              : {data['balance']:.2f} BGN",
            f"Savings rate         : {savings_rate_text}",
            "",
            "ACTIVITY",
            "-" * 42,
            f"Total transactions   : {transaction_count}",
            f"Income transactions  : {income_count}",
            f"Expense transactions : {expense_count}",
            f"Average expense      : {average_expense:.2f} BGN",
            "",
            "EXPENSES BY CATEGORY",
            "-" * 42,
        ]

        if not expenses:
            lines.append("No expenses for this month.")
        else:
            total_expense = data["expense"]
            for index, (category, amount) in enumerate(
                sorted(expenses.items(), key=lambda item: item[1], reverse=True),
                start=1,
            ):
                percentage = 0.0
                if total_expense > 0:
                    percentage = (amount / total_expense) * 100

                lines.append(
                    f"{index:>2}. {category:<18} {amount:>8.2f} BGN   ({percentage:>5.1f}%)"
                )

        lines.append("")
        lines.append("HIGHLIGHTS")
        lines.append("-" * 42)

        if top_category is not None:
            lines.append(
                f"Top expense category : {top_category[0]} ({top_category[1]:.2f} BGN)"
            )
        else:
            lines.append("Top expense category : N/A")

        if data["balance"] > 0:
            lines.append("Month status         : Positive balance")
        elif data["balance"] < 0:
            lines.append("Month status         : Negative balance")
        else:
            lines.append("Month status         : Break-even")

        return "\n".join(lines)
