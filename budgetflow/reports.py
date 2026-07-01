from __future__ import annotations

from pathlib import Path

from budgetflow.statistics import StatisticsService


class ReportGenerator:
    def __init__(self, statistics: StatisticsService, output_directory: str | Path = "reports") -> None:
        self.statistics = statistics
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def monthly_text_report(self, filename: str = "monthly_report.txt") -> Path:
        output_path = self.output_directory / filename
        monthly_summary = self.statistics.monthly_summary()

        lines = ["BudgetFlow monthly report", "=========================", ""]
        for month, data in monthly_summary.items():
            lines.append(f"{month}")
            lines.append(f"  Income:  {data['income']:.2f}")
            lines.append(f"  Expense: {data['expense']:.2f}")
            lines.append(f"  Balance: {data['balance']:.2f}")
            lines.append("")

        if not monthly_summary:
            lines.append("No transactions yet.")

        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        return output_path
