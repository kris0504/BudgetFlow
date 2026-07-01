from __future__ import annotations

from budgetflow.charts import ChartGenerator
from budgetflow.errors import BudgetFlowError
from budgetflow.reports import ReportGenerator
from budgetflow.services import FinanceManager


class ConsoleInterface:

    def __init__(self, manager: FinanceManager) -> None:
        self.manager = manager

    def run(self) -> None:
        while True:
            self._print_menu()
            choice = input("Choose option: ").strip()

            try:
                if choice == "1":
                    self._add_transaction("income")
                elif choice == "2":
                    self._add_transaction("expense")
                elif choice == "3":
                    self._list_transactions()
                elif choice == "4":
                    self._set_budget()
                elif choice == "5":
                    self._show_statistics()
                elif choice == "6":
                    self._generate_reports()
                elif choice == "0":
                    print("Goodbye!")
                    return
                else:
                    print("Unknown option.")
            except BudgetFlowError as error:
                print(f"Error: {error}")
            except ValueError as error:
                print(f"Error: {error}")

    @staticmethod
    def _print_menu() -> None:
        print("\nBudgetFlow")
        print("1. Add income")
        print("2. Add expense")
        print("3. List transactions")
        print("4. Set monthly budget")
        print("5. Show statistics")
        print("6. Generate reports and charts")
        print("0. Exit")

    def _add_transaction(self, transaction_type: str) -> None:
        amount = float(input("Amount: "))
        category = input("Category: ").strip()
        description = input("Description: ").strip()
        transaction_date = input("Date (YYYY-MM-DD, empty for today): ").strip() or None
        transaction = self.manager.add_transaction(
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            description=description,
            transaction_date=transaction_date,
        )
        print(f"Saved transaction with id {transaction.id}.")

    def _list_transactions(self) -> None:
        transactions = self.manager.list_transactions()
        if not transactions:
            print("No transactions yet.")
            return

        for transaction in transactions:
            print(
                f"#{transaction.id} | {transaction.transaction_date} | "
                f"{transaction.transaction_type.value:<7} | "
                f"{transaction.category:<12} | {transaction.amount:.2f} | "
                f"{transaction.description}"
            )

    def _set_budget(self) -> None:
        category = input("Category: ").strip()
        month = input("Month (YYYY-MM): ").strip()
        limit = float(input("Limit: "))
        budget = self.manager.set_budget(category, month, limit)
        print(f"Budget saved: {budget.category} {budget.month} {budget.limit:.2f}")

    def _show_statistics(self) -> None:
        statistics = self.manager.statistics()
        print(f"Total income:   {statistics.total_income():.2f}")
        print(f"Total expenses: {statistics.total_expenses():.2f}")
        print(f"Balance:        {statistics.balance():.2f}")
        print("Expenses by category:")
        for category, amount in statistics.expenses_by_category().items():
            print(f"  {category}: {amount:.2f}")

        print("Budgets:")
        for status in self.manager.all_budget_statuses():
            warning = " EXCEEDED" if status["is_exceeded"] else ""
            print(
                f"  {status['month']} {status['category']}: "
                f"spent {status['spent']:.2f} / {status['limit']:.2f}{warning}"
            )

    def _generate_reports(self) -> None:
        statistics = self.manager.statistics()
        report_path = ReportGenerator(statistics).monthly_text_report()
        print(f"Generated text report: {report_path}")

        chart_generator = ChartGenerator(statistics)
        try:
            print(f"Generated chart: {chart_generator.expenses_by_category_chart()}")
        except ValueError as error:
            print(f"Skipped expenses chart: {error}")

        try:
            print(f"Generated chart: {chart_generator.monthly_balance_chart()}")
        except ValueError as error:
            print(f"Skipped monthly chart: {error}")
