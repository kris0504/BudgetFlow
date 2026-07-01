class BudgetFlowError(Exception):
    """Base exception for the BudgetFlow application."""


class ValidationError(BudgetFlowError):
    """Raised when invalid data is passed to the application."""


class NotFoundError(BudgetFlowError):
    """Raised when an object cannot be found in storage."""
