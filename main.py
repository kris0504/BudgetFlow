from pathlib import Path

from budgetflow.gui import BudgetFlowApp
from budgetflow.services import FinanceManager
from budgetflow.storage import SQLiteStorage


def main() -> None:
    data_directory = Path("data")
    data_directory.mkdir(exist_ok=True)

    storage = SQLiteStorage(data_directory / "budgetflow.db")
    manager = FinanceManager(storage)
    app = BudgetFlowApp(manager)

    try:
        app.mainloop()
    finally:
        storage.close()


if __name__ == "__main__":
    main()
