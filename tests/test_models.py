import unittest
from datetime import date

from budgetflow.errors import ValidationError
from budgetflow.models import Budget, Transaction, TransactionType


class TestTransactionModel(unittest.TestCase):
    def test_creates_valid_expense_from_strings(self):
        transaction = Transaction(
            amount="12.345",
            category="  Food  ",
            transaction_type="expense",
            description="  lunch  ",
            transaction_date="2026-07-04",
        )

        self.assertEqual(transaction.amount, 12.35)
        self.assertEqual(transaction.category, "Food")
        self.assertEqual(transaction.transaction_type, TransactionType.EXPENSE)
        self.assertEqual(transaction.description, "lunch")
        self.assertEqual(transaction.transaction_date, date(2026, 7, 4))
        self.assertEqual(transaction.signed_amount, -12.35)

    def test_creates_valid_income_and_signed_amount_is_positive(self):
        transaction = Transaction(
            amount=1500,
            category="Salary",
            transaction_type=TransactionType.INCOME,
            transaction_date="2026-07-01",
        )

        self.assertEqual(transaction.signed_amount, 1500)

    def test_uses_today_when_date_is_missing(self):
        transaction = Transaction(
            amount=20,
            category="Other",
            transaction_type="expense",
        )

        self.assertEqual(transaction.transaction_date, date.today())

    def test_rejects_invalid_amounts(self):
        invalid_amounts = [0, -1, "abc", None]

        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                with self.assertRaises(ValidationError):
                    Transaction(
                        amount=amount,
                        category="Food",
                        transaction_type="expense",
                        transaction_date="2026-07-04",
                    )

    def test_rejects_empty_category(self):
        with self.assertRaises(ValidationError):
            Transaction(
                amount=10,
                category="   ",
                transaction_type="expense",
                transaction_date="2026-07-04",
            )

    def test_rejects_invalid_transaction_type(self):
        with self.assertRaises(ValidationError):
            Transaction(
                amount=10,
                category="Food",
                transaction_type="gift",
                transaction_date="2026-07-04",
            )

    def test_rejects_invalid_date_format(self):
        with self.assertRaises(ValidationError):
            Transaction(
                amount=10,
                category="Food",
                transaction_type="expense",
                transaction_date="04-07-2026",
            )

    def test_database_conversion_round_trip(self):
        transaction = Transaction(
            amount=19.99,
            category="Bills",
            transaction_type="expense",
            description="Internet",
            transaction_date="2026-07-03",
        )

        row = (7, *transaction.to_database_tuple())
        restored = Transaction.from_row(row)

        self.assertEqual(restored.id, 7)
        self.assertEqual(restored.amount, 19.99)
        self.assertEqual(restored.category, "Bills")
        self.assertEqual(restored.transaction_type, TransactionType.EXPENSE)
        self.assertEqual(restored.description, "Internet")
        self.assertEqual(restored.transaction_date, date(2026, 7, 3))


class TestBudgetModel(unittest.TestCase):
    def test_creates_valid_budget(self):
        budget = Budget(category="  Food ", month="2026-07", limit="500.126")

        self.assertEqual(budget.category, "Food")
        self.assertEqual(budget.month, "2026-07")
        self.assertEqual(budget.limit, 500.13)

    def test_rejects_invalid_month(self):
        with self.assertRaises(ValidationError):
            Budget(category="Food", month="2026/07", limit=500)

    def test_rejects_invalid_limit(self):
        with self.assertRaises(ValidationError):
            Budget(category="Food", month="2026-07", limit=0)

    def test_budget_from_row(self):
        budget = Budget.from_row((3, "Transport", "2026-08", 120.0))

        self.assertEqual(budget.id, 3)
        self.assertEqual(budget.category, "Transport")
        self.assertEqual(budget.month, "2026-08")
        self.assertEqual(budget.limit, 120.0)


if __name__ == "__main__":
    unittest.main()
