# BudgetFlow

BudgetFlow is a desktop Python application for managing personal finances.
It allows users to track income, expenses, categories, monthly budgets, statistics and reports through a graphical interface.

## Description

BudgetFlow helps users organize their personal finances in a simple and structured way.

The application supports adding income and expense transactions, organizing them by categories, setting monthly budgets and viewing financial summaries for selected months.

The project is built with a separated architecture between:

* graphical interface
* business logic
* data models
* statistics
* reports
* database storage
* tests

## Features

* Add income transactions
* Add expense transactions
* Edit existing transactions
* Delete transactions
* Search and filter transactions
* Manage transaction categories
* Set monthly budgets by category
* View budget status for a selected month
* View monthly income, expenses and balance
* View expenses grouped by category
* Generate monthly text reports
* Generate charts for monthly balance
* Generate charts for expenses by category
* Store data locally using SQLite
* Validate user input and show readable error messages
* Unit tests for the main application logic

## Technologies

* Python
* CustomTkinter
* SQLite
* matplotlib
* tkcalendar
* unittest

## Project Structure

```text
BudgetFlow/
├── budgetflow/
│   ├── charts.py
│   ├── cli.py
│   ├── errors.py
│   ├── gui.py
│   ├── models.py
│   ├── reports.py
│   ├── services.py
│   ├── statistics.py
│   └── storage.py
├── data/
├── reports/
├── tests/
│   ├── test_models.py
│   ├── test_reports_and_charts.py
│   ├── test_services.py
│   ├── test_statistics.py
│   └── test_storage.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Main Modules

### `models.py`

Contains the main data models used in the application, such as transactions, budgets and transaction types.

### `services.py`

Contains the main business logic of the application.

The graphical interface does not work directly with the database. Instead, it uses the service layer.

### `storage.py`

Handles saving, loading, updating and deleting data using SQLite.

### `statistics.py`

Calculates monthly totals, balances and expenses grouped by category.

### `reports.py`

Generates text reports based on the selected month.

### `charts.py`

Generates graphical charts using matplotlib.

### `gui.py`

Contains the CustomTkinter graphical interface.

### `tests/`

Contains unit tests for models, services, storage, statistics, reports and charts.

## Installation

Clone the repository:

```bash
git clone https://github.com/kris0504/BudgetFlow.git
cd BudgetFlow
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the project from the root directory:

```bash
python main.py
```

The application will start with a graphical interface.

## Running the Tests

Run all unit tests with:

```bash
python -m unittest discover -s tests
```

## Data Storage

BudgetFlow stores its data locally in an SQLite database.

The database is created automatically when the application is started.

SQLite is used because the application data is structured into transactions, categories and budgets. This makes a relational database more suitable than storing everything in a plain text file.

## Example Usage

1. Start the application.
2. Add income and expense transactions.
3. Create categories for the transactions.
4. Set monthly budgets for selected categories.
5. Open the statistics tab and select a month.
6. Generate charts or a monthly report.
7. Run the tests to verify the main logic.

## Testing

The project includes unit tests for the core logic of the application.

The tests focus on:

* models
* service layer
* storage layer
* statistics
* report generation
* chart generation

The graphical framework itself is not tested directly. Instead, the application logic is separated from the interface so it can be tested independently.

## Author

Kristiyan Todorov
