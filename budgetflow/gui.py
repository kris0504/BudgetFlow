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
        self.geometry("1050x780")
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

        ctk.CTkLabel(form, text="Delete transaction", font=("Arial", 15, "bold")).pack(
            padx=15, pady=(12, 4)
        )
        self.delete_transaction_id_entry = ctk.CTkEntry(
            form, placeholder_text="Transaction ID"
        )
        self.delete_transaction_id_entry.pack(padx=15, pady=8)

        self.delete_transaction_button = ctk.CTkButton(
            form,
            text="Delete transaction",
            command=self.delete_transaction,
            height=38,
        )
        self.delete_transaction_button.pack(padx=15, pady=(6, 8), fill="x")
        self.transactions_frame = ctk.CTkScrollableFrame(
            self.transactions_tab,
            fg_color="#1a1a1a",
        )
        self.transactions_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

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
        self.budget_category_menu.pack(padx=15, pady=(0, 8), fill="x")

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
        save_budget_button.pack(padx=15, pady=(12, 8), fill="x")

        self.budgets_frame = ctk.CTkScrollableFrame(
            self.budgets_tab,
            fg_color="#1a1a1a",
        )
        self.budgets_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

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
            padx=15, pady=(12, 8), fill="x"
        )

        ctk.CTkLabel(form, text="Delete category", font=("Arial", 16, "bold")).pack(
            padx=15, pady=(25, 6)
        )

        self.delete_category_menu = ctk.CTkOptionMenu(
            form, values=self._category_values()
        )
        self.delete_category_menu.pack(padx=15, pady=8, fill="x")

        ctk.CTkButton(form, text="Delete category", command=self.delete_category).pack(
            padx=15, pady=8, fill="x"
        )

        self.categories_frame = ctk.CTkScrollableFrame(
            self.categories_tab,
            fg_color="#1a1a1a",
        )
        self.categories_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

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

        self.statistics_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="#1a1a1a",
        )
        self.statistics_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def add_category(self) -> None:
        try:
            category = self.manager.add_category(self.new_category_entry.get())
            self.new_category_entry.delete(0, "end")
            self.refresh_data()
            self.category_menu.set(category)
            self.budget_category_menu.set(category)
            self.delete_category_menu.set(category)
            messagebox.showinfo("BudgetFlow", "Category saved successfully.")
        except BudgetFlowError as error:
            messagebox.showerror("BudgetFlow", str(error))

    def delete_category(self) -> None:
        category = self.delete_category_menu.get()
        if not messagebox.askyesno("BudgetFlow", f"Delete category '{category}'?"):
            return

        try:
            self.manager.delete_category(category)
            self.refresh_data()
            messagebox.showinfo("BudgetFlow", "Category deleted successfully.")
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

    def delete_transaction(self) -> None:
        try:
            transaction_id = int(self.delete_transaction_id_entry.get())
            if not messagebox.askyesno(
                "BudgetFlow", f"Delete transaction #{transaction_id}?"
            ):
                return

            self.manager.delete_transaction(transaction_id)
            self.delete_transaction_id_entry.delete(0, "end")
            self.refresh_data()
            messagebox.showinfo("BudgetFlow", "Transaction deleted successfully.")
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

    def refresh_data(self) -> None:
        self._refresh_category_menus()
        self._refresh_categories()
        self._refresh_transactions()
        self._refresh_budgets()
        self._refresh_statistics()

    def _refresh_category_menus(self) -> None:
        categories = self._category_values()

        current_delete_category = self.delete_category_menu.get()
        current_transaction_category = self.category_menu.get()
        current_budget_category = self.budget_category_menu.get()

        self.category_menu.configure(values=categories)
        self.budget_category_menu.configure(values=categories)
        self.delete_category_menu.configure(values=categories)

        if current_transaction_category in categories:
            self.category_menu.set(current_transaction_category)
        else:
            self.category_menu.set(categories[0])

        if current_budget_category in categories:
            self.budget_category_menu.set(current_budget_category)
        else:
            self.budget_category_menu.set(categories[0])
        if current_delete_category in categories:
            self.delete_category_menu.set(current_delete_category)
        else:
            self.delete_category_menu.set(categories[0])

    def _refresh_categories(self) -> None:
        for widget in self.categories_frame.winfo_children():
            widget.destroy()

        categories = self.manager.list_categories()

        if not categories:
            ctk.CTkLabel(
                self.categories_frame,
                text="No categories yet.",
                font=("Arial", 15),
                text_color="gray",
            ).pack(padx=15, pady=15, anchor="w")
            return

        for category in categories:
            card = ctk.CTkFrame(
                self.categories_frame,
                fg_color="#242424",
                corner_radius=10,
            )
            card.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                card,
                text=category,
                font=("Arial", 15, "bold"),
                anchor="w",
            ).pack(side="left", padx=12, pady=10)

            ctk.CTkLabel(
                card,
                text="Category",
                font=("Arial", 12),
                text_color="gray",
                anchor="e",
            ).pack(side="right", padx=12, pady=10)

    def _refresh_transactions(self) -> None:
        for widget in self.transactions_frame.winfo_children():
            widget.destroy()

        transactions = self.manager.list_transactions()

        if not transactions:
            ctk.CTkLabel(
                self.transactions_frame,
                text="No transactions yet.",
                font=("Arial", 15),
                text_color="gray",
            ).pack(padx=15, pady=15, anchor="w")
            return

        for transaction in transactions:
            transaction_type = transaction.transaction_type
            if hasattr(transaction_type, "value"):
                transaction_type = transaction_type.value

            date_text = transaction.transaction_date
            if hasattr(date_text, "isoformat"):
                date_text = date_text.isoformat()

            if transaction_type == "income":
                amount_text = f"+{transaction.amount:.2f} BGN"
                amount_color = "#4ade80"
            else:
                amount_text = f"-{transaction.amount:.2f} BGN"
                amount_color = "#f87171"

            card = ctk.CTkFrame(
                self.transactions_frame,
                fg_color="#242424",
                corner_radius=10,
            )
            card.pack(fill="x", padx=10, pady=6)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(
                top_row,
                text=f"#{transaction.id}  {transaction.category}",
                font=("Arial", 15, "bold"),
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                top_row,
                text=amount_text,
                font=("Arial", 15, "bold"),
                text_color=amount_color,
                anchor="e",
            ).pack(side="right")

            middle_row = ctk.CTkFrame(card, fg_color="transparent")
            middle_row.pack(fill="x", padx=12, pady=(0, 4))

            ctk.CTkLabel(
                middle_row,
                text=f"{date_text}  •  {transaction_type}",
                font=("Arial", 12),
                text_color="gray",
                anchor="w",
            ).pack(side="left")

            description = transaction.description
            if not description:
                description = "No description"

            ctk.CTkLabel(
                card,
                text=description,
                font=("Arial", 13),
                anchor="w",
                justify="left",
                wraplength=620,
            ).pack(fill="x", padx=12, pady=(0, 10))

    def _refresh_budgets(self) -> None:
        for widget in self.budgets_frame.winfo_children():
            widget.destroy()

        statuses = self.manager.all_budget_statuses()

        if not statuses:
            ctk.CTkLabel(
                self.budgets_frame,
                text="No budgets yet.",
                font=("Arial", 15),
                text_color="gray",
            ).pack(padx=15, pady=15, anchor="w")
            return

        for status in statuses:
            is_exceeded = status["is_exceeded"]

            if is_exceeded:
                remaining_text = f"Exceeded by {abs(status['remaining']):.2f} BGN"
                remaining_color = "#f87171"
                card_color = "#2b1d1d"
            else:
                remaining_text = f"Remaining {status['remaining']:.2f} BGN"
                remaining_color = "#4ade80"
                card_color = "#242424"

            card = ctk.CTkFrame(
                self.budgets_frame,
                fg_color=card_color,
                corner_radius=10,
            )
            card.pack(fill="x", padx=10, pady=6)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(
                top_row,
                text=f"{status['category']}",
                font=("Arial", 15, "bold"),
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                top_row,
                text=status["month"],
                font=("Arial", 13),
                text_color="gray",
                anchor="e",
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=f"Spent {status['spent']:.2f} / {status['limit']:.2f} BGN",
                font=("Arial", 13),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(2, 2))

            ctk.CTkLabel(
                card,
                text=remaining_text,
                font=("Arial", 13, "bold"),
                text_color=remaining_color,
                anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 10))

    def _refresh_statistics(self) -> None:
        for widget in self.statistics_frame.winfo_children():
            widget.destroy()

        statistics = self.manager.statistics()

        total_income = statistics.total_income()
        total_expenses = statistics.total_expenses()
        balance = statistics.balance()

        if balance >= 0:
            balance_color = "#4ade80"
        else:
            balance_color = "#f87171"

        summary_frame = ctk.CTkFrame(
            self.statistics_frame,
            fg_color="transparent",
        )
        summary_frame.pack(fill="x", padx=10, pady=(10, 6))

        income_card = ctk.CTkFrame(summary_frame, fg_color="#242424", corner_radius=10)
        income_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        ctk.CTkLabel(
            income_card,
            text="Total income",
            font=("Arial", 13),
            text_color="gray",
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            income_card,
            text=f"{total_income:.2f} BGN",
            font=("Arial", 18, "bold"),
            text_color="#4ade80",
        ).pack(anchor="w", padx=12, pady=(0, 10))

        expense_card = ctk.CTkFrame(summary_frame, fg_color="#242424", corner_radius=10)
        expense_card.pack(side="left", fill="both", expand=True, padx=6)

        ctk.CTkLabel(
            expense_card,
            text="Total expenses",
            font=("Arial", 13),
            text_color="gray",
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            expense_card,
            text=f"{total_expenses:.2f} BGN",
            font=("Arial", 18, "bold"),
            text_color="#f87171",
        ).pack(anchor="w", padx=12, pady=(0, 10))

        balance_card = ctk.CTkFrame(summary_frame, fg_color="#242424", corner_radius=10)
        balance_card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        ctk.CTkLabel(
            balance_card,
            text="Balance",
            font=("Arial", 13),
            text_color="gray",
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            balance_card,
            text=f"{balance:.2f} BGN",
            font=("Arial", 18, "bold"),
            text_color=balance_color,
        ).pack(anchor="w", padx=12, pady=(0, 10))

        expenses_title = ctk.CTkLabel(
            self.statistics_frame,
            text="Expenses by category",
            font=("Arial", 16, "bold"),
            anchor="w",
        )
        expenses_title.pack(fill="x", padx=12, pady=(16, 6))

        expenses = statistics.expenses_by_category()
        if not expenses:
            ctk.CTkLabel(
                self.statistics_frame,
                text="No expenses yet.",
                font=("Arial", 13),
                text_color="gray",
            ).pack(anchor="w", padx=12, pady=4)
        else:
            for category, amount in expenses.items():
                card = ctk.CTkFrame(
                    self.statistics_frame,
                    fg_color="#242424",
                    corner_radius=10,
                )
                card.pack(fill="x", padx=10, pady=4)

                ctk.CTkLabel(
                    card,
                    text=category,
                    font=("Arial", 14, "bold"),
                    anchor="w",
                ).pack(side="left", padx=12, pady=8)

                ctk.CTkLabel(
                    card,
                    text=f"{amount:.2f} BGN",
                    font=("Arial", 14),
                    text_color="#f87171",
                    anchor="e",
                ).pack(side="right", padx=12, pady=8)

        monthly_title = ctk.CTkLabel(
            self.statistics_frame,
            text="Monthly summary",
            font=("Arial", 16, "bold"),
            anchor="w",
        )
        monthly_title.pack(fill="x", padx=12, pady=(16, 6))

        monthly_summary = statistics.monthly_summary()
        if not monthly_summary:
            ctk.CTkLabel(
                self.statistics_frame,
                text="No transactions yet.",
                font=("Arial", 13),
                text_color="gray",
            ).pack(anchor="w", padx=12, pady=4)
        else:
            for month, data in monthly_summary.items():
                month_balance = data["balance"]
                if month_balance >= 0:
                    month_balance_color = "#4ade80"
                else:
                    month_balance_color = "#f87171"

                card = ctk.CTkFrame(
                    self.statistics_frame,
                    fg_color="#242424",
                    corner_radius=10,
                )
                card.pack(fill="x", padx=10, pady=4)

                ctk.CTkLabel(
                    card,
                    text=month,
                    font=("Arial", 14, "bold"),
                    anchor="w",
                ).pack(fill="x", padx=12, pady=(8, 2))

                ctk.CTkLabel(
                    card,
                    text=(
                        f"Income {data['income']:.2f} BGN  |  "
                        f"Expense {data['expense']:.2f} BGN  |  "
                        f"Balance {data['balance']:.2f} BGN"
                    ),
                    font=("Arial", 13),
                    text_color=month_balance_color,
                    anchor="w",
                ).pack(fill="x", padx=12, pady=(0, 8))

    def _clear_transaction_form(self) -> None:
        self.amount_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        # self.date_entry.delete(0, "end")
        self.type_menu.set("expense")

    def _clear_budget_form(self) -> None:
        # self.budget_category_entry.delete(0, "end")
        # self.budget_month_entry.delete(0, "end")
        self.budget_limit_entry.delete(0, "end")
