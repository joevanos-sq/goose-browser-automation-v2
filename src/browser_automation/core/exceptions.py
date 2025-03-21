"""Core exceptions for browser automation."""
from typing import Any, Optional


class BrowserAutomationError(Exception):
    """Base exception for browser automation errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.code = code
        self.details = details
        self.name = 'BrowserAutomationError'


class ElementNotFoundError(BrowserAutomationError):
    """Raised when an element cannot be found."""
    
    def __init__(
        self,
        message: str,
        selector: str,
        details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code='ELEMENT_NOT_FOUND',
            details={'selector': selector, **details} if details else {'selector': selector}
        )
        self.name = 'ElementNotFoundError'


class WebComponentError(BrowserAutomationError):
    """Raised when there's an issue with web components."""
    
    def __init__(
        self,
        message: str,
        component: str,
        details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code='WEB_COMPONENT_ERROR',
            details={'component': component, **details} if details else {'component': component}
        )
        self.name = 'WebComponentError'


class NavigationError(BrowserAutomationError):
    """Raised when navigation fails."""
    
    def __init__(
        self,
        message: str,
        url: str,
        details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code='NAVIGATION_ERROR',
            details={'url': url, **details} if details else {'url': url}
        )
        self.name = 'NavigationError'


class InteractionError(BrowserAutomationError):
    """Raised when an interaction fails."""
    
    def __init__(
        self,
        message: str,
        action: str,
        details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code='INTERACTION_ERROR',
            details={'action': action, **details} if details else {'action': action}
        )
        self.name = 'InteractionError'