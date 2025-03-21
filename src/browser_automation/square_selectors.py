"""Square-specific selectors and configurations."""

class SquareSelectors:
    """Selectors for Square's web interface."""
    LOGIN = {
        'email_input': '[data-test-form] input',  # Email input field
        'password_input': 'input[type="password"]',  # Password input field
        'continue_button': 'market-button',  # Continue button
        'submit_button': 'market-button'  # Sign in button
    }

    LOADING_INDICATORS = [
        '[role="progressbar"]',
        '[aria-busy="true"]',
        '.loading',
        '#loading',
        '[data-loading="true"]',
        '.spinner',
        '[role="status"]'
    ]

    WEB_COMPONENTS = [
        'market-button',
        'market-input-text',
        'market-select',
        'market-dropdown',
        'sq-button',
        'sq-input',
        'sq-form',
        'sq-payment-form'
    ]

class SquareConfig:
    """Configuration for Square environments."""
    ENVIRONMENTS = {
        'staging': {
            'domain': 'squareupstaging.com',
            'headers': {
                'X-Square-Environment': 'staging'
            }
        },
        'production': {
            'domain': 'squareup.com',
            'headers': {}
        }
    }