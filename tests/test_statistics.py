import unittest

from budgetflow.models import Transaction
from budgetflow.statistics import StatisticsService


class TestStatisticsService(unittest.TestCase):
    def setUp(self):
        self.transactions = [
            Transaction(1000, "Salary", "income", "July salary", "2026-07-01"),
            Transaction(200, "Food", "expense", "Groceries", "2026-07-02"),
            Transaction(50.56, "Food", "expense", "Restaurant", "2026-07-03"),
            Transaction(100, "Transport", "expense", "Train", "2026-06-30"),
            Transaction(100, "Freelance", "income", "Small job", "2026-06-15"),
        ]
        self.statistics = StatisticsService(self.transactions)

    def test_calculates_totals_and_balance(self):
        self.assertEqual(self.statistics.total_income(), 1100)
        self.assertEqual(self.statistics.total_expenses(), 350.56)
        self.assertEqual(self.statistics.balance(), 749.44)

    def test_groups_expenses_by_category(self):
        self.assertEqual(
            self.statistics.expenses_by_category(),
            {"Food": 250.56, "Transport": 100.0},
        )

    def test_groups_income_by_category(self):
        self.assertEqual(
            self.statistics.income_by_category(),
            {"Salary": 1000.0, "Freelance": 100.0},
        )

    def test_monthly_summary_is_sorted_from_newest_month(self):
        self.assertEqual(
            self.statistics.monthly_summary(),
            {
                "2026-07": {"income": 1000.0, "expense": 250.56, "balance": 749.44},
                "2026-06": {"income": 100.0, "expense": 100.0, "balance": 0.0},
            },
        )

    def test_top_expense_categories_respects_limit(self):
        self.assertEqual(
            self.statistics.top_expense_categories(limit=1),
            [("Food", 250.56)],
        )

    def test_empty_statistics_return_zero_values(self):
        statistics = StatisticsService([])

        self.assertEqual(statistics.total_income(), 0)
        self.assertEqual(statistics.total_expenses(), 0)
        self.assertEqual(statistics.balance(), 0)
        self.assertEqual(statistics.expenses_by_category(), {})
        self.assertEqual(statistics.income_by_category(), {})
        self.assertEqual(statistics.monthly_summary(), {})
        self.assertEqual(statistics.top_expense_categories(), [])


if __name__ == "__main__":
    unittest.main()
