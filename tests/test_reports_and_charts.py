import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from budgetflow.charts import ChartGenerator
from budgetflow.models import Transaction
from budgetflow.reports import ReportGenerator
from budgetflow.statistics import StatisticsService


class ReportsAndChartsTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_directory = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()


class TestReportGenerator(ReportsAndChartsTestCase):
    def test_monthly_text_report_contains_summary(self):
        statistics = StatisticsService(
            [
                Transaction(1000, "Salary", "income", "Paycheck", "2026-07-01"),
                Transaction(250, "Food", "expense", "Groceries", "2026-07-02"),
            ]
        )
        generator = ReportGenerator(statistics, self.output_directory)

        report_path = generator.monthly_text_report("report.txt")
        content = report_path.read_text(encoding="utf-8")

        self.assertTrue(report_path.exists())
        self.assertIn("BudgetFlow monthly report", content)
        self.assertIn("2026-07", content)
        self.assertIn("Income:  1000.00", content)
        self.assertIn("Expense: 250.00", content)
        self.assertIn("Balance: 750.00", content)

    def test_monthly_text_report_handles_empty_transactions(self):
        generator = ReportGenerator(StatisticsService([]), self.output_directory)

        report_path = generator.monthly_text_report("empty.txt")
        content = report_path.read_text(encoding="utf-8")

        self.assertIn("No transactions yet.", content)


class TestChartGenerator(ReportsAndChartsTestCase):
    def test_expenses_by_category_chart_creates_png_file(self):
        statistics = StatisticsService(
            [
                Transaction(250, "Food", "expense", "Groceries", "2026-07-02"),
                Transaction(100, "Transport", "expense", "Bus", "2026-07-03"),
            ]
        )
        generator = ChartGenerator(statistics, self.output_directory)

        chart_path = generator.expenses_by_category_chart("expenses.png")

        self.assertTrue(chart_path.exists())
        self.assertGreater(chart_path.stat().st_size, 0)

    def test_monthly_balance_chart_creates_png_file(self):
        statistics = StatisticsService(
            [
                Transaction(1000, "Salary", "income", "Paycheck", "2026-07-01"),
                Transaction(250, "Food", "expense", "Groceries", "2026-07-02"),
                Transaction(100, "Food", "expense", "June groceries", "2026-06-20"),
            ]
        )
        generator = ChartGenerator(statistics, self.output_directory)

        chart_path = generator.monthly_balance_chart("balance.png")

        self.assertTrue(chart_path.exists())
        self.assertGreater(chart_path.stat().st_size, 0)

    def test_charts_raise_value_error_when_there_is_no_data_to_visualize(self):
        generator = ChartGenerator(StatisticsService([]), self.output_directory)

        with self.assertRaises(ValueError):
            generator.expenses_by_category_chart("expenses.png")

        with self.assertRaises(ValueError):
            generator.monthly_balance_chart("balance.png")


if __name__ == "__main__":
    unittest.main()
