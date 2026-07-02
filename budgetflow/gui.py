from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk
from tkcalendar import DateEntry

from budgetflow.charts import ChartGenerator
from budgetflow.errors import BudgetFlowError
from budgetflow.reports import ReportGenerator
from budgetflow.services import FinanceManager


class BudgetFlowApp(ctk.CTk):

    def __init__(self, manager: FinanceManager) -> None:
        super().__init__()
        self.manager = manager

        self.title("BudgetFlow")
        self.geometry("950x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._create_widgets()
        self.refresh_data()

    def _create_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.transactions_tab = self.tabs.add("Transactions")
        self.budgets_tab = self.tabs.add("Budgets")
        self.categories_tab = self.tabs.add("Categories")
        self.statistics_tab = self.tabs.add("Statistics")

        self._create_transactions_tab()
        self._create_budgets_tab()
        self._create_categories_tab()
        self._create_statistics_tab()

    def _category_values(self) -> list[str]:
        categories = self.manager.list_categories()
        if categories:
            return categories
        return ["Other"]

    def _create_transactions_tab(self) -> None:
        self.transactions_tab.grid_columnconfigure(0, weight=0)
        self.transactions_tab.grid_columnconfigure(1, weight=1)
        self.transactions_tab.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(self.transactions_tab)
        form.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        ctk.CTkLabel(form, text="Add transaction", font=("Arial", 18, "bold")).pack(
            padx=15, pady=(15, 10)
        )

        self.amount_entry = ctk.CTkEntry(form, placeholder_text="Amount")
        self.amount_entry.pack(padx=15, pady=8)

        ctk.CTkLabel(form, text="Category").pack(padx=15, pady=(8, 2))
        self.category_menu = ctk.CTkOptionMenu(form, values=self._category_values())
        self.category_menu.pack(padx=15, pady=(0, 8))

        self.type_menu = ctk.CTkOptionMenu(form, values=["expense", "income"])
        self.type_menu.set("expense")
        self.type_menu.pack(padx=15, pady=8)

        ctk.CTkLabel(form, text="Date").pack(padx=15, pady=(8, 2))
        self.date_entry = DateEntry(
            form,
            date_pattern="yyyy-mm-dd",
            width=18,
            background="#1f6aa5",
            foreground="white",
            borderwidth=2,
        )
        self.date_entry.pack(padx=15, pady=(0, 8))

        self.description_entry = ctk.CTkEntry(form, placeholder_text="Description")
        self.description_entry.pack(padx=15, pady=8)

        add_button = ctk.CTkButton(form, text="Save", command=self.add_transaction)
        add_button.pack(padx=15, pady=(12, 8))

        refresh_button = ctk.CTkButton(form, text="Refresh", command=self.refresh_data)
        refresh_button.pack(padx=15, pady=8)

        self.transactions_box = ctk.CTkTextbox(self.transactions_tab)
        self.transactions_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def _create_budgets_tab(self) -> None:
        self.budgets_tab.grid_columnconfigure(0, weight=0)
        self.budgets_tab.grid_columnconfigure(1, weight=1)
        self.budgets_tab.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(self.budgets_tab)
        form.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        ctk.CTkLabel(form, text="Monthly budget", font=("Arial", 18, "bold")).pack(
            padx=15, pady=(15, 10)
        )

        ctk.CTkLabel(form, text="Category").pack(padx=15, pady=(8, 2))
        self.budget_category_menu = ctk.CTkOptionMenu(
            form, values=self._category_values()
        )
        self.budget_category_menu.pack(padx=15, pady=(0, 8))

        ctk.CTkLabel(form, text="Budget month").pack(padx=15, pady=(8, 2))
        self.budget_month_entry = DateEntry(
            form,
            date_pattern="yyyy-mm-dd",
            width=18,
            background="#1f6aa5",
            foreground="white",
            borderwidth=2,
        )
        self.budget_month_entry.pack(padx=15, pady=(0, 8))

        self.budget_limit_entry = ctk.CTkEntry(form, placeholder_text="Limit")
        self.budget_limit_entry.pack(padx=15, pady=8)

        save_budget_button = ctk.CTkButton(
            form, text="Save budget", command=self.save_budget
        )
        save_budget_button.pack(padx=15, pady=(12, 8))

        self.budgets_box = ctk.CTkTextbox(self.budgets_tab)
        self.budgets_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def _create_categories_tab(self) -> None:
        self.categories_tab.grid_columnconfigure(0, weight=0)
        self.categories_tab.grid_columnconfigure(1, weight=1)
        self.categories_tab.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(self.categories_tab)
        form.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        ctk.CTkLabel(form, text="Create category", font=("Arial", 18, "bold")).pack(
            padx=15, pady=(15, 10)
        )

        self.new_category_entry = ctk.CTkEntry(form, placeholder_text="Category name")
        self.new_category_entry.pack(padx=15, pady=8)

        ctk.CTkButton(form, text="Add category", command=self.add_category).pack(
            padx=15, pady=(12, 8)
        )

        self.categories_box = ctk.CTkTextbox(self.categories_tab)
        self.categories_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def _create_statistics_tab(self) -> None:
        self.statistics_tab.grid_columnconfigure(0, weight=1)
        self.statistics_tab.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(self.statistics_tab)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        button_frame = ctk.CTkFrame(frame)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            button_frame, text="Refresh statistics", command=self.refresh_data
        ).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(
            button_frame, text="Generate report", command=self.generate_report
        ).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(
            button_frame, text="Generate charts", command=self.generate_charts
        ).pack(side="left", padx=8, pady=8)

        self.statistics_box = ctk.CTkTextbox(frame)
        self.statistics_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def add_category(self) -> None:
        try:
            category = self.manager.add_category(self.new_category_entry.get())
            self.new_category_entry.delete(0, "end")
            self.refresh_data()
            self.category_menu.set(category)
            self.budget_category_menu.set(category)
            messagebox.showinfo("BudgetFlow", "Category saved successfully.")
        except BudgetFlowError as error:
            messagebox.showerror("BudgetFlow", str(error))

    def add_transaction(self) -> None:
        try:
            self.manager.add_transaction(
                amount=float(self.amount_entry.get()),
                category=self.category_menu.get(),
                transaction_type=self.type_menu.get(),
                description=self.description_entry.get(),
                transaction_date=self.date_entry.get_date().isoformat(),
            )
            self._clear_transaction_form()
            self.refresh_data()
            messagebox.showinfo("BudgetFlow", "Transaction saved successfully.")
        except (BudgetFlowError, ValueError) as error:
            messagebox.showerror("BudgetFlow", str(error))

    def save_budget(self) -> None:
        try:
            self.manager.set_budget(
                category=self.budget_category_menu.get(),
                month=self.budget_month_entry.get_date().strftime("%Y-%m"),
                limit=float(self.budget_limit_entry.get()),
            )
            self._clear_budget_form()
            self.refresh_data()
            messagebox.showinfo("BudgetFlow", "Budget saved successfully.")
        except (BudgetFlowError, ValueError) as error:
            messagebox.showerror("BudgetFlow", str(error))

    def refresh_data(self) -> None:
        self._refresh_category_menus()
        self._refresh_categories()
        self._refresh_transactions()
        self._refresh_budgets()
        self._refresh_statistics()

    def _refresh_category_menus(self) -> None:
        categories = self._category_values()

        current_transaction_category = self.category_menu.get()
        current_budget_category = self.budget_category_menu.get()

        self.category_menu.configure(values=categories)
        self.budget_category_menu.configure(values=categories)

        if current_transaction_category in categories:
            self.category_menu.set(current_transaction_category)
        else:
            self.category_menu.set(categories[0])

        if current_budget_category in categories:
            self.budget_category_menu.set(current_budget_category)
        else:
            self.budget_category_menu.set(categories[0])

    def _refresh_categories(self) -> None:
        self.categories_box.configure(state="normal")
        self.categories_box.delete("1.0", "end")

        categories = self.manager.list_categories()
        if not categories:
            self.categories_box.insert("end", "No categories yet.")
        else:
            for category in categories:
                self.categories_box.insert("end", f"- {category}\n")

        self.categories_box.configure(state="disabled")

    def _refresh_transactions(self) -> None:
        self.transactions_box.configure(state="normal")
        self.transactions_box.delete("1.0", "end")

        transactions = self.manager.list_transactions()
        if not transactions:
            self.transactions_box.insert("end", "No transactions yet.")
        else:
            for transaction in transactions:
                self.transactions_box.insert(
                    "end",
                    f"#{transaction.id} | {transaction.transaction_date} | "
                    f"{transaction.transaction_type.value:<7} | "
                    f"{transaction.category:<15} | {transaction.amount:>8.2f} | "
                    f"{transaction.description}\n",
                )

        self.transactions_box.configure(state="disabled")

    def _refresh_budgets(self) -> None:
        self.budgets_box.configure(state="normal")
        self.budgets_box.delete("1.0", "end")

        statuses = self.manager.all_budget_statuses()
        if not statuses:
            self.budgets_box.insert("end", "No budgets yet.")
        else:
            for status in statuses:
                warning = "  !!! EXCEEDED" if status["is_exceeded"] else ""
                self.budgets_box.insert(
                    "end",
                    f"{status['month']} | {status['category']:<15} | "
                    f"spent {status['spent']:>8.2f} / {status['limit']:>8.2f} | "
                    f"remaining {status['remaining']:>8.2f}{warning}\n",
                )

        self.budgets_box.configure(state="disabled")

    def _refresh_statistics(self) -> None:
        statistics = self.manager.statistics()

        lines = [
            f"Total income:   {statistics.total_income():.2f}",
            f"Total expenses: {statistics.total_expenses():.2f}",
            f"Balance:        {statistics.balance():.2f}",
            "",
            "Expenses by category:",
        ]

        expenses = statistics.expenses_by_category()
        if expenses:
            for category, amount in expenses.items():
                lines.append(f"  {category}: {amount:.2f}")
        else:
            lines.append("  No expenses yet.")

        lines.append("")
        lines.append("Monthly summary:")
        monthly_summary = statistics.monthly_summary()
        if monthly_summary:
            for month, data in monthly_summary.items():
                lines.append(
                    f"  {month}: income {data['income']:.2f}, "
                    f"expense {data['expense']:.2f}, balance {data['balance']:.2f}"
                )
        else:
            lines.append("  No transactions yet.")

        self.statistics_box.configure(state="normal")
        self.statistics_box.delete("1.0", "end")
        self.statistics_box.insert("end", "\n".join(lines))
        self.statistics_box.configure(state="disabled")

    def generate_report(self) -> None:
        try:
            path = ReportGenerator(self.manager.statistics()).monthly_text_report()
            messagebox.showinfo("BudgetFlow", f"Report generated: {path}")
        except ValueError as error:
            messagebox.showerror("BudgetFlow", str(error))

    def generate_charts(self) -> None:
        try:
            generator = ChartGenerator(self.manager.statistics())
            paths = [generator.monthly_balance_chart()]
            try:
                paths.append(generator.expenses_by_category_chart())
            except ValueError:
                pass
            messagebox.showinfo(
                "BudgetFlow",
                "Charts generated:\n" + "\n".join(str(path) for path in paths),
            )
        except ValueError as error:
            messagebox.showerror("BudgetFlow", str(error))

    def _clear_transaction_form(self) -> None:
        self.amount_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        # self.date_entry.delete(0, "end")
        self.type_menu.set("expense")

    def _clear_budget_form(self) -> None:
        # self.budget_category_entry.delete(0, "end")
        # self.budget_month_entry.delete(0, "end")
        self.budget_limit_entry.delete(0, "end")
