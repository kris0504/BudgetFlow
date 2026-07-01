from __future__ import annotations

from pathlib import Path

from budgetflow.statistics import StatisticsService


class ChartGenerator:
    """Generates image files with charts."""

    def __init__(
        self, statistics: StatisticsService, output_directory: str | Path = "reports"
    ) -> None:
        self.statistics = statistics
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def expenses_by_category_chart(
        self, filename: str = "expenses_by_category.png"
    ) -> Path:
        import matplotlib.pyplot as plt

        data = self.statistics.expenses_by_category()
        output_path = self.output_directory / filename

        if not data:
            raise ValueError("There are no expenses to visualize.")

        categories = list(data.keys())
        amounts = list(data.values())

        plt.figure(figsize=(8, 5))
        plt.bar(categories, amounts)
        plt.title("Expenses by category")
        plt.xlabel("Category")
        plt.ylabel("Amount")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        return output_path

    def monthly_balance_chart(self, filename: str = "monthly_balance.png") -> Path:
        import matplotlib.pyplot as plt

        summary = self.statistics.monthly_summary()
        output_path = self.output_directory / filename

        if not summary:
            raise ValueError("There are no transactions to visualize.")

        months = list(reversed(summary.keys()))
        balances = [summary[month]["balance"] for month in months]

        plt.figure(figsize=(8, 5))
        plt.plot(months, balances, marker="o")
        plt.title("Monthly balance")
        plt.xlabel("Month")
        plt.ylabel("Balance")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        return output_path
