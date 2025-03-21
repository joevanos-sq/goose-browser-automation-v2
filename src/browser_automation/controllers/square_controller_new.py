"""Square login automation using new infrastructure."""
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import os
import json
from playwright.async_api import Page, TimeoutError

from ..core.web_component_handler import WebComponentHandler
from ..core.element_locator import ElementLocator
from ..core.exceptions import (
    ElementNotFoundError,
    WebComponentError,
    NavigationError,
    InteractionError
)

logger = logging.getLogger(__name__)


class SquareController:
    """Controls Square-specific automation tasks."""
    
    def __init__(self, page: Page):
        """Initialize with a page instance."""
        self.page = page
        self.web_components = WebComponentHandler(page)
        self.locator = ElementLocator(page)
        self.debug_dir = Path(os.path.expanduser("~/.goose/debug"))
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_debug_info(self, name: str, data: Dict[str, Any]) -> None:
        """Save debug information to a file."""
        path = self.debug_dir / f"{name}.json"
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved debug info to {path}")
        
    async def save_debug_screenshot(self, name: str) -> None:
        """Save a screenshot for debugging."""
        path = self.debug_dir / f"{name}.png"
        await self.page.screenshot(path=str(path))
        logger.debug(f"Saved screenshot to {path}")
        
    async def handle_cookie_consent(self) -> None:
        """Handle cookie consent banner if present."""
        try:
            if await self.locator.is_element_present({
                'id': 'accept-recommended-btn-handler'
            }):
                button = await self.locator.find_element({
                    'id': 'accept-recommended-btn-handler'
                })
                await button.click()
                await self.locator.wait_for_element(
                    {'id': 'onetrust-banner-sdk'},
                    state='hidden'
                )
                logger.debug("Handled cookie consent")
        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")
            
    async def wait_for_square_components(self) -> None:
        """Wait for Square-specific web components."""
        try:
            await self.web_components.wait_for_components([
                'market-button',
                'market-input-text'
            ])
            logger.debug("Square web components are ready")
        except WebComponentError as e:
            logger.error(f"Failed waiting for Square components: {e}")
            raise
            
    async def fill_email(self, email: str) -> None:
        """Fill in the email field."""
        try:
            email_input = await self.locator.find_element({
                'id': 'mpui-combo-field-input'
            })
            await email_input.fill(email)
            logger.debug(f"Filled email: {email}")
        except ElementNotFoundError as e:
            logger.error(f"Failed to fill email: {e}")
            raise InteractionError(
                message="Failed to fill email field",
                action="fill_email",
                details={'email': email, 'error': str(e)}
            )
            
    async def click_continue(self) -> None:
        """Click the continue button."""
        try:
            # Try multiple selectors for the continue button
            selectors = [
                {'test_id': 'login-email-next-button'},
                {'role': 'button', 'text': 'Continue'},
                {'tag': 'market-button', 'test_id': 'login-email-next-button'}
            ]
            
            for selector in selectors:
                try:
                    button = await self.locator.find_element(selector)
                    await button.click()
                    logger.debug(f"Clicked continue button with selector: {selector}")
                    return
                except ElementNotFoundError:
                    continue
                    
            raise ElementNotFoundError(
                message="Continue button not found with any selector",
                selector=str(selectors)
            )
            
        except Exception as e:
            logger.error(f"Failed to click continue: {e}")
            raise InteractionError(
                message="Failed to click continue button",
                action="click_continue",
                details={'error': str(e)}
            )
            
    async def fill_password(self, password: str) -> None:
        """Fill in the password field."""
        try:
            password_input = await self.locator.find_element({
                'type': 'password'
            })
            await password_input.fill(password)
            logger.debug("Filled password field")
        except ElementNotFoundError as e:
            logger.error(f"Failed to fill password: {e}")
            raise InteractionError(
                message="Failed to fill password field",
                action="fill_password",
                details={'error': str(e)}
            )
            
    async def click_sign_in(self) -> None:
        """Click the sign in button."""
        try:
            button = await self.locator.find_element({
                'test_id': 'sign-in-button'
            })
            await button.click()
            logger.debug("Clicked sign in button")
        except ElementNotFoundError as e:
            logger.error(f"Failed to click sign in: {e}")
            raise InteractionError(
                message="Failed to click sign in button",
                action="click_sign_in",
                details={'error': str(e)}
            )
            
    async def verify_login_success(self) -> bool:
        """Verify successful login."""
        try:
            await self.locator.wait_for_element({
                'test_id': 'dashboard-container'
            })
            logger.info("Login successful - dashboard found")
            return True
        except ElementNotFoundError:
            logger.error("Login verification failed - dashboard not found")
            return False
            
    async def login(self, email: str, password: str) -> bool:
        """
        Handle Square login flow.
        
        Args:
            email: Square account email
            password: Square account password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Set default timeout
            self.page.set_default_timeout(30000)
            
            # Navigate to login page
            logger.info("Navigating to login page...")
            await self.page.goto(
                'https://app.squareupstaging.com/login',
                wait_until='networkidle'
            )
            await self.save_debug_screenshot("01_initial_page")
            
            # Handle cookie consent
            logger.info("Handling cookie consent...")
            await self.handle_cookie_consent()
            
            # Wait for web components
            logger.info("Waiting for Square components...")
            await self.wait_for_square_components()
            
            # Fill email
            logger.info("Entering email...")
            await self.fill_email(email)
            await self.save_debug_screenshot("02_email_entered")
            
            # Click continue
            logger.info("Clicking continue...")
            await self.click_continue()
            await self.save_debug_screenshot("03_after_continue")
            
            # Fill password
            logger.info("Entering password...")
            await self.fill_password(password)
            await self.save_debug_screenshot("04_password_entered")
            
            # Click sign in
            logger.info("Clicking sign in...")
            await self.click_sign_in()
            await self.save_debug_screenshot("05_after_signin")
            
            # Verify login
            return await self.verify_login_success()
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            await self.save_debug_screenshot("error")
            return False