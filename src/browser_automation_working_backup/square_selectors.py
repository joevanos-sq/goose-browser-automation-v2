"""Square-specific selectors and utilities."""

SQUARE_SELECTORS = {
    # Login form elements
    'email_input': '[data-test-form] input[type="email"]',
    'password_input': '[data-test-form] input[type="password"]',
    'continue_button': '[data-test-form] market-button[data-testid="continue-button"]',
    'sign_in_button': '[data-test-form] market-button[data-testid="sign-in-button"]',
    
    # Loading indicators
    'loading': '[role="progressbar"]',
    
    # Common Square components
    'market_button': 'market-button',
    'market_input_text': 'market-input-text',
    'market_select': 'market-select',
    'market_dropdown': 'market-dropdown',
    'sq_button': 'sq-button',
    'sq_input': 'sq-input',
    'sq_form': 'sq-form',
    'sq_payment_form': 'sq-payment-form'
}

# Wait times in milliseconds
TIMEOUTS = {
    'navigation': 30000,
    'element': 10000,
    'animation': 1000
}

# URLs
URLS = {
    'staging_login': 'https://app.squareupstaging.com/login',
    'prod_login': 'https://app.squareup.com/login'
}