from __future__ import annotations

from budgetflow.statistics import StatisticsService


class ReportGenerator:
    """Builds text reports from financial statistics."""

    def __init__(self, statistics: StatisticsService) -> None:
        self.statistics = statistics

    def monthly_text_report(self, month: str | None = None) -> str:
        if month is not None:
            return self._single_month_report(month)

        monthly_summary = self.statistics.monthly_summary()

        lines = ["BudgetFlow monthly report", "=========================", ""]
        for current_month, data in monthly_summary.items():
            lines.append(f"{current_month}")
            lines.append(f"  Income:  {data['income']:.2f}")
            lines.append(f"  Expense: {data['expense']:.2f}")
            lines.append(f"  Balance: {data['balance']:.2f}")
            lines.append("")

        if not monthly_summary:
            lines.append("No transactions yet.")

        return "\n".join(lines)

    def _single_month_report(self, month: str) -> str:
        data = self.statistics.monthly_totals(month)
        expenses = self.statistics.expenses_by_category(month)

        lines = [
            f"BudgetFlow report for {month}",
            "============================",
            "",
            f"Income:  {data['income']:.2f}",
            f"Expense: {data['expense']:.2f}",
            f"Balance: {data['balance']:.2f}",
            "",
            "Expenses by category:",
        ]

        if not expenses:
            lines.append("  No expenses for this month.")
        else:
            for category, amount in expenses.items():
                lines.append(f"  {category}: {amount:.2f}")

        return "\n".join(lines)
