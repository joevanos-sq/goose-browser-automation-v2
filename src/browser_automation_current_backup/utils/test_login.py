"""Browser automation test utilities."""
import os
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from ..square_selectors import SQUARE_SELECTORS, TIMEOUTS, URLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_square_login(email: str, password: str, headless: bool = False):
    """
    Test Square login flow using Playwright's sync API for easier debugging.
    """
    debug_dir = Path(os.path.expanduser("~/.goose/debug"))
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser with debugging options
        browser = p.chromium.launch(
            headless=headless,
            devtools=True,
            args=[
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
        
        # Create context with security bypass
        context = browser.new_context(
            bypass_csp=True,
            ignore_https_errors=True,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        # Enable verbose logging
        context.set_default_timeout(60000)
        page = context.new_page()
        
        page.on('console', lambda msg: logger.info(f'Browser console {msg.type}: {msg.text}'))
        page.on('pageerror', lambda err: logger.error(f'Browser page error: {err}'))
        
        try:
            # Navigate to login page
            logger.info("Navigating to login page...")
            page.goto(URLS['staging_login'], wait_until='networkidle')
            page.screenshot(path=str(debug_dir / "01_initial_load.png"))
            
            # Wait for JavaScript initialization
            logger.info("Waiting for JavaScript...")
            page.wait_for_function("""
                typeof window.customElements !== 'undefined' &&
                document.readyState === 'complete'
            """)
            page.screenshot(path=str(debug_dir / "02_js_ready.png"))
            
            # Handle cookie consent if present
            if page.locator('#onetrust-banner-sdk').is_visible():
                logger.info("Handling cookie consent...")
                page.click('#accept-recommended-btn-handler')
                page.wait_for_selector('#onetrust-banner-sdk', state='hidden')
                page.screenshot(path=str(debug_dir / "03_cookies_accepted.png"))
            
            # Wait for and fill email
            logger.info("Entering email...")
            email_input = page.locator('[data-testid="username-input"]')
            email_input.wait_for(state='visible')
            email_input.fill(email)
            page.screenshot(path=str(debug_dir / "04_email_entered.png"))
            
            # Click continue
            logger.info("Clicking continue...")
            continue_button = page.locator('[data-testid="login-email-next-button"]')
            continue_button.wait_for(state='visible')
            continue_button.click()
            
            # Handle reCAPTCHA if present
            logger.info("Checking for reCAPTCHA...")
            if page.locator('.grecaptcha-badge').is_visible():
                logger.info("reCAPTCHA detected")
                page.screenshot(path=str(debug_dir / "05a_recaptcha_detected.png"))
                
                # Wait for reCAPTCHA to be ready
                page.wait_for_function("""
                    typeof window.grecaptcha !== 'undefined' &&
                    window.grecaptcha.enterprise !== undefined
                """)
                
                # Execute reCAPTCHA
                page.evaluate("""() => {
                    return new Promise((resolve) => {
                        grecaptcha.enterprise.ready(() => {
                            grecaptcha.enterprise.execute(
                                document.querySelector('.grecaptcha-badge').dataset.sitekey,
                                {action: 'login'}
                            ).then(resolve);
                        });
                    });
                }""")
                
                page.screenshot(path=str(debug_dir / "05b_recaptcha_handled.png"))
            
            # Wait for navigation after continue
            page.wait_for_load_state('networkidle')
            time.sleep(2)  # Additional wait for stability
            page.screenshot(path=str(debug_dir / "05c_after_continue.png"))
            
            # Check for error messages
            error = page.locator('[data-testid="error-message"]')
            if error.is_visible():
                error_text = error.text_content()
                logger.error(f"Login error: {error_text}")
                page.screenshot(path=str(debug_dir / "05d_login_error.png"))
                return False
            
            # Wait for password field with retry
            logger.info("Waiting for password field...")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    password_input = page.locator('[data-testid="password-input"]')
                    password_input.wait_for(state='visible', timeout=20000)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Retry {attempt + 1}/{max_retries} waiting for password field")
                    time.sleep(2)
            
            page.screenshot(path=str(debug_dir / "06_password_field_ready.png"))
            
            # Fill password
            logger.info("Entering password...")
            password_input.fill(password)
            page.screenshot(path=str(debug_dir / "07_password_entered.png"))
            
            # Click sign in
            logger.info("Clicking sign in...")
            sign_in_button = page.locator('[data-testid="sign-in-button"]')
            sign_in_button.wait_for(state='visible')
            sign_in_button.click()
            
            # Wait for navigation and verify login
            page.wait_for_load_state('networkidle')
            page.screenshot(path=str(debug_dir / "08_after_signin.png"))
            
            # Check for success
            logger.info("Checking login status...")
            try:
                page.wait_for_selector('[data-testid="dashboard-container"]', timeout=TIMEOUTS['navigation'])
                page.screenshot(path=str(debug_dir / "09_login_success.png"))
                logger.info("Login successful!")
                return True
            except Exception as e:
                logger.error(f"Login failed: {e}")
                page.screenshot(path=str(debug_dir / "09_login_failed.png"))
                return False
                
        except Exception as e:
            logger.error(f"Test failed: {e}")
            page.screenshot(path=str(debug_dir / "error.png"))
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    # Run test with provided credentials
    test_square_login(
        email="joev+goosetestfree1@squareup.com",
        password="password",
        headless=False
    )