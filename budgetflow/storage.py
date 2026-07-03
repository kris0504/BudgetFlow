from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from budgetflow.errors import NotFoundError, ValidationError
from budgetflow.models import Budget, Transaction

DEFAULT_CATEGORIES = (
    "Food",
    "Transport",
    "Salary",
    "Bills",
    "Shopping",
    "Entertainment",
    "Health",
    "Other",
)


class SQLiteStorage:

    def __init__(self, database_path: str | Path = "data/budgetflow.db") -> None:
        self.database_path = database_path
        self._connection = sqlite3.connect(database_path)
        self._create_tables()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteStorage":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def _create_tables(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT NOT NULL,
                transaction_date TEXT NOT NULL
            )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                month TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                UNIQUE(category, month)
            )
            """)
        self._connection.commit()
        self._seed_default_categories()

    def _seed_default_categories(self) -> None:
        for category in DEFAULT_CATEGORIES:
            self.add_category(category)

    def add_category(self, name: str) -> str:
        category = Transaction._validate_category(name)
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)",
            (category,),
        )
        self._connection.commit()
        return category

    def list_categories(self) -> list[str]:
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT name FROM categories
            UNION
            SELECT category FROM transactions
            UNION
            SELECT category FROM budgets
            ORDER BY name COLLATE NOCASE
            """)
        return [row[0] for row in cursor.fetchall()]

    def delete_category(self, name: str) -> None:
        category = Transaction._validate_category(name)
        cursor = self._connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM transactions WHERE category = ?",
            (category,),
        )
        transactions_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM budgets WHERE category = ?",
            (category,),
        )
        budgets_count = cursor.fetchone()[0]

        if transactions_count > 0 or budgets_count > 0:
            raise ValidationError(
                "Cannot delete category because it is used by transactions or budgets."
            )

        cursor.execute("DELETE FROM categories WHERE name = ?", (category,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Category {category} was not found.")

        self._connection.commit()

    def add_transaction(self, transaction: Transaction) -> Transaction:
        self.add_category(transaction.category)
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO transactions
                (amount, category, transaction_type, description, transaction_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            transaction.to_database_tuple(),
        )
        self._connection.commit()
        transaction.id = cursor.lastrowid
        return transaction

    def update_transaction(
        self, transaction_id: int, transaction: Transaction
    ) -> Transaction:
        self.add_category(transaction.category)
        cursor = self._connection.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET amount = ?, category = ?, transaction_type = ?, description = ?, transaction_date = ?
            WHERE id = ?
            """,
            (*transaction.to_database_tuple(), transaction_id),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Transaction with id {transaction_id} was not found.")
        self._connection.commit()
        transaction.id = transaction_id
        return transaction

    def delete_transaction(self, transaction_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Transaction with id {transaction_id} was not found.")
        self._connection.commit()

    def get_transaction(self, transaction_id: int) -> Transaction:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT id, amount, category, transaction_type, description, transaction_date
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise NotFoundError(f"Transaction with id {transaction_id} was not found.")
        return Transaction.from_row(row)

    def list_transactions(self) -> list[Transaction]:
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT id, amount, category, transaction_type, description, transaction_date
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
            """)
        return [Transaction.from_row(row) for row in cursor.fetchall()]

    def search_transactions(
        self,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[Transaction]:
        query = """
            SELECT id, amount, category, transaction_type, description, transaction_date
            FROM transactions
            WHERE 1 = 1
        """
        params: list[str] = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)

        query += " ORDER BY transaction_date DESC, id DESC"
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return [Transaction.from_row(row) for row in cursor.fetchall()]

    def set_budget(self, budget: Budget) -> Budget:
        self.add_category(budget.category)
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO budgets (category, month, limit_amount)
            VALUES (?, ?, ?)
            ON CONFLICT(category, month)
            DO UPDATE SET limit_amount = excluded.limit_amount
            """,
            (budget.category, budget.month, budget.limit),
        )
        self._connection.commit()
        return self.get_budget(budget.category, budget.month)

    def get_budget(self, category: str, month: str) -> Budget:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT id, category, month, limit_amount
            FROM budgets
            WHERE category = ? AND month = ?
            """,
            (category, month),
        )
        row = cursor.fetchone()
        if row is None:
            raise NotFoundError(f"Budget for {category} in {month} was not found.")
        return Budget.from_row(row)

    def list_budgets(self) -> list[Budget]:
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT id, category, month, limit_amount
            FROM budgets
            ORDER BY month DESC, category ASC
            """)
        return [Budget.from_row(row) for row in cursor.fetchall()]

    def clear_all(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM budgets")
        cursor.execute("DELETE FROM categories")
        self._connection.commit()
        self._seed_default_categories()
