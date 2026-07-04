import tempfile
import unittest
from pathlib import Path

from budgetflow.errors import NotFoundError, ValidationError
from budgetflow.models import TransactionType
from budgetflow.storage import DEFAULT_CATEGORIES, SQLiteStorage


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "budgetflow-test.db"
        self.storage = SQLiteStorage(self.database_path)

    def tearDown(self):
        self.storage.close()
        self.temp_dir.cleanup()


class TestSQLiteStorageCategories(StorageTestCase):
    def test_default_categories_are_seeded(self):
        categories = self.storage.list_categories()

        for category in DEFAULT_CATEGORIES:
            self.assertIn(category, categories)

    def test_add_category_trims_name_and_ignores_duplicates(self):
        self.storage.add_category("  Travel  ")
        self.storage.add_category("Travel")

        categories = self.storage.list_categories()
        self.assertEqual(categories.count("Travel"), 1)

    def test_delete_unused_category(self):
        self.storage.add_category("Travel")
        self.storage.delete_category("Travel")

        self.assertNotIn("Travel", self.storage.list_categories())

    def test_delete_missing_category_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            self.storage.delete_category("Missing")

    def test_cannot_delete_category_used_by_transaction(self):
        transaction = self.storage.add_transaction(
            self._transaction("Food", "expense", "2026-07-04")
        )
        self.assertIsNotNone(transaction.id)

        with self.assertRaises(ValidationError):
            self.storage.delete_category("Food")

    def test_cannot_delete_category_used_by_budget(self):
        self.storage.set_budget(self._budget("Transport", "2026-07", 100))

        with self.assertRaises(ValidationError):
            self.storage.delete_category("Transport")

    @staticmethod
    def _transaction(category, transaction_type, transaction_date):
        from budgetflow.models import Transaction

        return Transaction(
            amount=10,
            category=category,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
        )

    @staticmethod
    def _budget(category, month, limit):
        from budgetflow.models import Budget

        return Budget(category=category, month=month, limit=limit)


class TestSQLiteStorageTransactions(StorageTestCase):
    def test_add_get_list_update_and_delete_transaction(self):
        created = self.storage.add_transaction(
            self._transaction(25.50, "Food", "expense", "Dinner", "2026-07-04")
        )

        self.assertIsNotNone(created.id)
        loaded = self.storage.get_transaction(created.id)
        self.assertEqual(loaded.amount, 25.50)
        self.assertEqual(loaded.category, "Food")
        self.assertEqual(loaded.transaction_type, TransactionType.EXPENSE)
        self.assertEqual(loaded.description, "Dinner")

        updated = self.storage.update_transaction(
            created.id,
            self._transaction(30, "Entertainment", "expense", "Cinema", "2026-07-05"),
        )
        self.assertEqual(updated.id, created.id)
        self.assertEqual(self.storage.get_transaction(created.id).category, "Entertainment")
        self.assertEqual(self.storage.get_transaction(created.id).amount, 30)

        self.storage.delete_transaction(created.id)
        self.assertEqual(self.storage.list_transactions(), [])
        with self.assertRaises(NotFoundError):
            self.storage.get_transaction(created.id)

    def test_missing_transaction_operations_raise_not_found(self):
        with self.assertRaises(NotFoundError):
            self.storage.get_transaction(999)

        with self.assertRaises(NotFoundError):
            self.storage.update_transaction(
                999,
                self._transaction(20, "Food", "expense", "Missing", "2026-07-04"),
            )

        with self.assertRaises(NotFoundError):
            self.storage.delete_transaction(999)

    def test_list_transactions_is_sorted_by_newest_date_then_newest_id(self):
        older = self.storage.add_transaction(
            self._transaction(10, "Food", "expense", "Older", "2026-07-01")
        )
        first_same_day = self.storage.add_transaction(
            self._transaction(20, "Food", "expense", "First same day", "2026-07-04")
        )
        newest_same_day = self.storage.add_transaction(
            self._transaction(30, "Food", "expense", "Newest same day", "2026-07-04")
        )

        listed_ids = [transaction.id for transaction in self.storage.list_transactions()]
        self.assertEqual(listed_ids, [newest_same_day.id, first_same_day.id, older.id])

    def test_search_transactions_filters_by_category_and_date_range(self):
        self.storage.add_transaction(
            self._transaction(10, "Food", "expense", "June food", "2026-06-30")
        )
        july_food = self.storage.add_transaction(
            self._transaction(20, "Food", "expense", "July food", "2026-07-04")
        )
        self.storage.add_transaction(
            self._transaction(30, "Transport", "expense", "July transport", "2026-07-04")
        )

        results = self.storage.search_transactions(
            category="Food",
            start_date="2026-07-01",
            end_date="2026-07-31",
        )

        self.assertEqual([transaction.id for transaction in results], [july_food.id])

    @staticmethod
    def _transaction(amount, category, transaction_type, description, transaction_date):
        from budgetflow.models import Transaction

        return Transaction(
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            description=description,
            transaction_date=transaction_date,
        )


class TestSQLiteStorageBudgets(StorageTestCase):
    def test_set_budget_creates_then_updates_same_category_and_month(self):
        created = self.storage.set_budget(self._budget("Food", "2026-07", 500))
        updated = self.storage.set_budget(self._budget("Food", "2026-07", 650))

        self.assertEqual(created.category, "Food")
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.limit, 650)
        self.assertEqual(len(self.storage.list_budgets()), 1)

    def test_list_budgets_is_sorted_by_month_descending_and_category(self):
        june_transport = self.storage.set_budget(self._budget("Transport", "2026-06", 100))
        july_food = self.storage.set_budget(self._budget("Food", "2026-07", 500))
        july_bills = self.storage.set_budget(self._budget("Bills", "2026-07", 200))

        listed = self.storage.list_budgets()
        self.assertEqual(
            [(budget.id, budget.category, budget.month) for budget in listed],
            [
                (july_bills.id, "Bills", "2026-07"),
                (july_food.id, "Food", "2026-07"),
                (june_transport.id, "Transport", "2026-06"),
            ],
        )

    def test_delete_budget_removes_existing_budget(self):
        self.storage.set_budget(self._budget("Food", "2026-07", 500))
        self.storage.delete_budget("Food", "2026-07")

        with self.assertRaises(NotFoundError):
            self.storage.get_budget("Food", "2026-07")

    def test_delete_missing_budget_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            self.storage.delete_budget("Food", "2026-07")

    @staticmethod
    def _budget(category, month, limit):
        from budgetflow.models import Budget

        return Budget(category=category, month=month, limit=limit)


class TestSQLiteStoragePersistence(StorageTestCase):
    def test_data_persists_when_database_is_reopened(self):
        transaction = self.storage.add_transaction(
            self._transaction(100, "Salary", "income", "Paycheck", "2026-07-01")
        )
        budget = self.storage.set_budget(self._budget("Food", "2026-07", 500))
        self.storage.close()

        reopened = SQLiteStorage(self.database_path)
        try:
            self.assertEqual(reopened.get_transaction(transaction.id).description, "Paycheck")
            self.assertEqual(reopened.get_budget(budget.category, budget.month).limit, 500)
        finally:
            reopened.close()

    def test_clear_all_removes_user_data_and_restores_default_categories(self):
        self.storage.add_category("Travel")
        self.storage.add_transaction(
            self._transaction(100, "Salary", "income", "Paycheck", "2026-07-01")
        )
        self.storage.set_budget(self._budget("Food", "2026-07", 500))

        self.storage.clear_all()

        self.assertEqual(self.storage.list_transactions(), [])
        self.assertEqual(self.storage.list_budgets(), [])
        self.assertNotIn("Travel", self.storage.list_categories())
        for category in DEFAULT_CATEGORIES:
            self.assertIn(category, self.storage.list_categories())

    @staticmethod
    def _transaction(amount, category, transaction_type, description, transaction_date):
        from budgetflow.models import Transaction

        return Transaction(
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            description=description,
            transaction_date=transaction_date,
        )

    @staticmethod
    def _budget(category, month, limit):
        from budgetflow.models import Budget

        return Budget(category=category, month=month, limit=limit)


if __name__ == "__main__":
    unittest.main()
