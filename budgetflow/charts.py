from __future__ import annotations

from matplotlib.figure import Figure

from budgetflow.statistics import StatisticsService


class ChartGenerator:

    def __init__(self, statistics: StatisticsService) -> None:
        self.statistics = statistics

    def expenses_by_category_chart(self, month: str | None = None) -> Figure:
        data = self.statistics.expenses_by_category(month)

        if not data:
            if month is None:
                raise ValueError("There are no expenses to visualize.")
            raise ValueError(f"There are no expenses to visualize for {month}.")

        categories = list(data.keys())
        amounts = list(data.values())

        figure = Figure(figsize=(8, 5), dpi=100)
        axes = figure.add_subplot(111)
        axes.bar(categories, amounts)

        if month is None:
            title = "Expenses by category"
        else:
            title = f"Expenses by category for {month}"

        axes.set_title(title)
        axes.set_xlabel("Category")
        axes.set_ylabel("Amount")
        axes.tick_params(axis="x", rotation=30)
        figure.tight_layout()

        return figure

    def monthly_balance_chart(self) -> Figure:
        summary = self.statistics.monthly_summary()

        if not summary:
            raise ValueError("There are no transactions to visualize.")

        months = list(reversed(summary.keys()))
        balances = [summary[month]["balance"] for month in months]

        figure = Figure(figsize=(8, 5), dpi=100)
        axes = figure.add_subplot(111)
        axes.plot(months, balances, marker="o")
        axes.set_title("Monthly balance")
        axes.set_xlabel("Month")
        axes.set_ylabel("Balance")
        figure.tight_layout()

        return figure
