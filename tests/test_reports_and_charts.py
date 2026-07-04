import os
import unittest

os.environ.setdefault("MPLBACKEND", "Agg")

from matplotlib.figure import Figure

from budgetflow.charts import ChartGenerator
from budgetflow.models import Transaction
from budgetflow.reports import ReportGenerator
from budgetflow.statistics import StatisticsService


class TestReportGenerator(unittest.TestCase):
    def test_monthly_text_report_contains_summary(self):
        statistics = StatisticsService(
            [
                Transaction(1000, "Salary", "income", "Paycheck", "2026-07-01"),
                Transaction(250, "Food", "expense", "Groceries", "2026-07-02"),
            ]
        )
        generator = ReportGenerator(statistics)

        content = generator.monthly_text_report("2026-07")

        self.assertIn("BudgetFlow report for 2026-07", content)
        self.assertIn("Income:  1000.00", content)
        self.assertIn("Expense: 250.00", content)
        self.assertIn("Balance: 750.00", content)
        self.assertIn("Food: 250.00", content)

    def test_monthly_text_report_handles_empty_transactions(self):
        generator = ReportGenerator(StatisticsService([]))

        content = generator.monthly_text_report()

        self.assertIn("No transactions yet.", content)

    def test_monthly_text_report_handles_month_without_expenses(self):
        generator = ReportGenerator(StatisticsService([]))

        content = generator.monthly_text_report("2026-07")

        self.assertIn("BudgetFlow report for 2026-07", content)
        self.assertIn("No expenses for this month.", content)


class TestChartGenerator(unittest.TestCase):
    def test_expenses_by_category_chart_returns_figure_for_selected_month(self):
        statistics = StatisticsService(
            [
                Transaction(250, "Food", "expense", "Groceries", "2026-07-02"),
                Transaction(100, "Transport", "expense", "Bus", "2026-06-03"),
            ]
        )
        generator = ChartGenerator(statistics)

        figure = generator.expenses_by_category_chart("2026-07")

        self.assertIsInstance(figure, Figure)
        self.assertEqual(figure.axes[0].get_title(), "Expenses by category for 2026-07")

    def test_monthly_balance_chart_returns_figure(self):
        statistics = StatisticsService(
            [
                Transaction(1000, "Salary", "income", "Paycheck", "2026-07-01"),
                Transaction(250, "Food", "expense", "Groceries", "2026-07-02"),
                Transaction(100, "Food", "expense", "June groceries", "2026-06-20"),
            ]
        )
        generator = ChartGenerator(statistics)

        figure = generator.monthly_balance_chart()

        self.assertIsInstance(figure, Figure)
        self.assertEqual(figure.axes[0].get_title(), "Monthly balance")

    def test_charts_raise_value_error_when_there_is_no_data_to_visualize(self):
        generator = ChartGenerator(StatisticsService([]))

        with self.assertRaises(ValueError):
            generator.expenses_by_category_chart()

        with self.assertRaises(ValueError):
            generator.expenses_by_category_chart("2026-07")

        with self.assertRaises(ValueError):
            generator.monthly_balance_chart()


if __name__ == "__main__":
    unittest.main()
