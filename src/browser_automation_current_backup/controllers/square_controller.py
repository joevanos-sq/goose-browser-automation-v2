"""Square login controller with enhanced component handling."""
from typing import Dict, Any, Optional
from playwright.async_api import Page
import logging
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Configure logging
logger = logging.getLogger(__name__)

class SquareController:
    """Controls Square-specific browser automation."""
    
    # Specific selectors for Square login flow
    SELECTORS = {
        'email_input': {
            'primary': "market-input-text[data-testid='email-input']",
            'fallback': "market-input-text[name='email']"
        },
        'password_input': {
            'primary': "market-input-text[data-testid='password-input']",
            'fallback': "market-input-text[name='password']"
        },
        'continue_button': {
            'primary': "market-button[data-testid='login-email-submit-button']",
            'fallback': "market-button[name='continue-button']"
        },
        'sign_in_button': {
            'primary': "market-button[data-testid='login-password-submit-button']",
            'fallback': [
                "market-button[name='sign-in-button']",
                ".split-login-password-view-actions market-button",
                "market-button[data-test-submit]"
            ]
        }
    }
    
    def __init__(self, page: Page):
        """Initialize with Playwright page."""
        self.page = page
        
    async def login(self, email: str, password: str) -> bool:
        """
        Execute Square login flow with enhanced error handling.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Starting Square login flow")
            
            # Navigate to login page
            logger.info("Navigating to login page")
            await self.page.goto('https://app.squareupstaging.com/login')
            
            # Enter email
            logger.info(f"Entering email: {email}")
            email_input = self.page.get_by_role('textbox', name='Email or phone number')
            await email_input.fill(email)
            
            # Click continue
            logger.info("Clicking continue button")
            continue_button = self.page.get_by_role('button', name='Continue')
            await continue_button.click()
            
            # Wait for password field
            logger.info("Waiting for password field")
            await self.page.wait_for_timeout(1000)  # Give the page transition time
            
            # Enter password
            logger.info("Entering password")
            password_input = self.page.get_by_role('textbox', name='Password')
            await password_input.fill(password)
            
            # Click sign in
            logger.info("Clicking sign in button")
            sign_in_button = self.page.get_by_role('button', name='Sign in')
            await sign_in_button.click()
            
            # Verify login success
            logger.info("Verifying login success")
            if await self.verify_login_success():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            await self.save_error_state()
            return False
            
    async def verify_login_success(self) -> bool:
        """Verify successful login with multiple checks."""
        try:
            # Wait for URL change
            await self.page.wait_for_url(
                "**/dashboard**",
                timeout=5000
            )
            
            # Check for common post-login elements
            dashboard_indicators = [
                ".dashboard-header",
                "[data-testid='dashboard-content']",
                "text=Welcome back"
            ]
            
            for indicator in dashboard_indicators:
                try:
                    await self.page.wait_for_selector(
                        indicator,
                        timeout=2000
                    )
                    return True
                except Exception:
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Login verification failed: {str(e)}")
            return False
            
    async def save_error_state(self) -> None:
        """Save page state for debugging."""
        try:
            # Take screenshot
            await self.page.screenshot(
                path='login_failure.png'
            )
            
            # Save page content
            content = await self.page.content()
            with open('login_failure.html', 'w') as f:
                f.write(content)
                
            # Log current URL and title
            logger.debug(f"Current URL: {self.page.url}")
            logger.debug(f"Page title: {await self.page.title()}")
            
        except Exception as e:
            logger.error(f"Failed to save debug state: {str(e)}")