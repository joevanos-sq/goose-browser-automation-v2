"""Square-specific selectors and configurations."""
from typing import Dict, Any

class SquareSelectors:
    """Selectors for Square's web interface components."""
    
    # Login page selectors
    LOGIN = {
        'email_input': 'input[data-testid="username-input"]',  # Email input field
        'email_next_button': 'market-button[data-testid="login-email-next-button"]',  # Next button after email
        'password_input': 'input[type="password"]',  # Password input field
        'password_next_button': 'market-button[data-testid="login-password-next-button"]',  # Next button after password
        'sign_in_button': 'market-button[data-testid="login-password-next-button"]'  # Same as password next button
    }
    
    # Square web components
    WEB_COMPONENTS = {
        'market-button': {
            'tag': 'market-button',
            'shadow': True,
            'inner_button': 'button',
            'loading_state': '[role="progressbar"]'
        },
        'market-input-text': {
            'tag': 'market-input-text',
            'shadow': True,
            'inner_input': 'input',
            'error_message': '.error-message'
        },
        'market-input-password': {
            'tag': 'market-input-password',
            'shadow': True,
            'inner_input': 'input[type="password"]',
            'error_message': '.error-message'
        },
        'market-select': {
            'tag': 'market-select',
            'shadow': True,
            'inner_select': 'select',
            'options_container': '.options'
        },
        'market-dropdown': {
            'tag': 'market-dropdown',
            'shadow': True,
            'trigger': '.trigger',
            'menu': '.menu'
        }
    }
    
    # Common UI elements
    COMMON = {
        'loading_indicators': [
            '[role="progressbar"]',
            '[aria-busy="true"]',
            '.loading',
            '.spinner'
        ],
        'error_messages': [
            '.error-message',
            '[role="alert"]',
            '[data-testid="error-message"]'
        ],
        'modals': {
            'container': '[role="dialog"]',
            'close_button': '[aria-label="Close"]'
        }
    }
    
    @classmethod
    def get_component_selector(cls, component_name: str) -> Dict[str, Any]:
        """Get full selector configuration for a component."""
        return cls.WEB_COMPONENTS.get(component_name, {})