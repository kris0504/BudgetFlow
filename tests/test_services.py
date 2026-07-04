import tempfile
import unittest
from pathlib import Path

from budgetflow.errors import NotFoundError
from budgetflow.models import TransactionType
from budgetflow.services import FinanceManager
from budgetflow.storage import SQLiteStorage


class FinanceManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = SQLiteStorage(Path(self.temp_dir.name) / "budgetflow-test.db")
        self.manager = FinanceManager(self.storage)

    def tearDown(self):
        self.storage.close()
        self.temp_dir.cleanup()


class TestFinanceManagerTransactions(FinanceManagerTestCase):
    def test_add_income_and_expense_through_manager(self):
        income = self.manager.add_income(1200, "Salary", "July salary", "2026-07-01")
        expense = self.manager.add_expense(150, "Food", "Groceries", "2026-07-02")

        transactions = self.manager.list_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertEqual(income.transaction_type, TransactionType.INCOME)
        self.assertEqual(expense.transaction_type, TransactionType.EXPENSE)
        self.assertEqual(self.manager.statistics().balance(), 1050)

    def test_update_delete_and_search_transactions_through_manager(self):
        transaction = self.manager.add_expense(80, "Food", "Groceries", "2026-07-02")

        updated = self.manager.update_transaction(
            transaction.id,
            95,
            "Shopping",
            "expense",
            "Clothes",
            "2026-07-03",
        )

        self.assertEqual(updated.category, "Shopping")
        self.assertEqual(
            [result.id for result in self.manager.search_transactions(category="Shopping")],
            [transaction.id],
        )

        self.manager.delete_transaction(transaction.id)
        self.assertEqual(self.manager.list_transactions(), [])


class TestFinanceManagerBudgets(FinanceManagerTestCase):
    def test_budget_status_when_budget_is_not_exceeded(self):
        self.manager.set_budget("Food", "2026-07", 500)
        self.manager.add_expense(120, "Food", "Groceries", "2026-07-02")
        self.manager.add_income(1000, "Food", "Refund-like income", "2026-07-03")
        self.manager.add_expense(100, "Food", "Previous month", "2026-06-30")
        self.manager.add_expense(50, "Transport", "Bus", "2026-07-04")

        status = self.manager.budget_status("Food", "2026-07")

        self.assertEqual(
            status,
            {"limit": 500.0, "spent": 120.0, "remaining": 380.0, "is_exceeded": False},
        )

    def test_budget_status_when_budget_is_exceeded(self):
        self.manager.set_budget("Food", "2026-07", 100)
        self.manager.add_expense(80, "Food", "Groceries", "2026-07-02")
        self.manager.add_expense(45, "Food", "Dinner", "2026-07-05")

        status = self.manager.budget_status("Food", "2026-07")

        self.assertEqual(status["spent"], 125)
        self.assertEqual(status["remaining"], -25)
        self.assertTrue(status["is_exceeded"])

    def test_all_budget_statuses_contains_category_and_month(self):
        self.manager.set_budget("Food", "2026-07", 500)
        self.manager.add_expense(100, "Food", "Groceries", "2026-07-02")

        statuses = self.manager.all_budget_statuses()

        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0]["category"], "Food")
        self.assertEqual(statuses[0]["month"], "2026-07")
        self.assertEqual(statuses[0]["spent"], 100)

    def test_delete_budget_through_manager(self):
        self.manager.set_budget("Food", "2026-07", 500)
        self.manager.delete_budget("Food", "2026-07")

        with self.assertRaises(NotFoundError):
            self.manager.budget_status("Food", "2026-07")


class TestFinanceManagerCategories(FinanceManagerTestCase):
    def test_add_list_and_delete_category_through_manager(self):
        self.manager.add_category("Travel")
        self.assertIn("Travel", self.manager.list_categories())

        self.manager.delete_category("Travel")
        self.assertNotIn("Travel", self.manager.list_categories())


if __name__ == "__main__":
    unittest.main()
