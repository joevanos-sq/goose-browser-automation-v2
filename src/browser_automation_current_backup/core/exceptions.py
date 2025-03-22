"""Browser automation exceptions."""
from typing import Optional


class BrowserError(Exception):
    """Base exception for browser automation errors."""
    pass


class ElementNotFoundError(BrowserError):
    """Raised when an element cannot be found."""
    def __init__(self, selector: str, message: Optional[str] = None):
        self.selector = selector
        super().__init__(
            message or f"Element not found: {selector}"
        )


class ComponentError(BrowserError):
    """Base exception for web component errors."""
    def __init__(self, component_type: str, message: str):
        self.component_type = component_type
        super().__init__(f"{component_type} error: {message}")


class SquareComponentError(ComponentError):
    """Raised when there's an error with Square web components."""
    def __init__(self, component_type: str, message: str):
        super().__init__(f"Square {component_type}", message)


class LoginError(BrowserError):
    """Raised when login process fails."""
    pass


class InvalidStateTransition(BrowserError):
    """Raised when an invalid state transition is attempted."""
    pass