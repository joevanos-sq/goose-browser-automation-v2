"""Square login automation using new infrastructure."""
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import os
import json
import asyncio
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
            # First wait for the form wrapper
            await self.page.wait_for_selector(
                '[data-testid="login-form-wrapper"]',
                state='visible',
                timeout=30000
            )
            
            # Then wait for specific web components
            await self.web_components.wait_for_components([
                'market-button',
                'market-input-text'
            ])
            
            # Additional wait for JavaScript initialization
            await self.page.wait_for_function("""
                () => {
                    return window.customElements &&
                           document.querySelector('market-button') &&
                           document.querySelector('market-input-text') &&
                           !document.querySelector('.noscript');
                }
            """)
            
            logger.debug("Square web components are ready")
            
        except Exception as e:
            logger.error(f"Failed waiting for Square components: {e}")
            raise WebComponentError(
                message="Failed to initialize Square components",
                component="market-button, market-input-text",
                details={'error': str(e)}
            )
            
    async def fill_email(self, email: str) -> None:
        """Fill in the email field."""
        try:
            # Wait for the input field
            await self.page.wait_for_selector(
                '#mpui-combo-field-input',
                state='visible',
                timeout=30000
            )
            
            # Fill using JavaScript for reliability
            await self.page.evaluate(f"""
                () => {{
                    const input = document.querySelector('#mpui-combo-field-input');
                    if (input) {{
                        input.value = "{email}";
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            """)
            
            # Verify the value was set
            value = await self.page.evaluate("""
                () => document.querySelector('#mpui-combo-field-input').value
            """)
            
            if value != email:
                raise InteractionError(
                    message="Failed to set email value",
                    action="fill_email",
                    details={'expected': email, 'actual': value}
                )
                
            logger.debug(f"Filled email: {email}")
            
        except Exception as e:
            logger.error(f"Failed to fill email: {e}")
            raise InteractionError(
                message="Failed to fill email field",
                action="fill_email",
                details={'email': email, 'error': str(e)}
            )
            
    async def click_continue(self) -> None:
        """Click the continue button."""
        try:
            # Wait for button to be ready
            await self.page.wait_for_selector(
                '[data-testid="login-email-next-button"]',
                state='visible',
                timeout=30000
            )
            
            # Get button info before clicking
            button_info = await self.page.evaluate("""
                () => {
                    const button = document.querySelector('[data-testid="login-email-next-button"]');
                    return {
                        isVisible: button.offsetParent !== null,
                        isEnabled: !button.disabled,
                        hasClickHandler: button.onclick !== null,
                        rect: button.getBoundingClientRect()
                    };
                }
            """)
            
            logger.debug(f"Continue button info: {button_info}")
            
            # Try multiple click strategies
            strategies = [
                # 1. Direct click
                lambda: self.page.click('[data-testid="login-email-next-button"]'),
                
                # 2. JavaScript click
                lambda: self.page.evaluate("""
                    () => {
                        const button = document.querySelector('[data-testid="login-email-next-button"]');
                        if (button) {
                            button.click();
                        }
                    }
                """),
                
                # 3. Dispatch click event
                lambda: self.page.evaluate("""
                    () => {
                        const button = document.querySelector('[data-testid="login-email-next-button"]');
                        if (button) {
                            const event = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            button.dispatchEvent(event);
                        }
                    }
                """),
                
                # 4. Click with position
                lambda: self.page.mouse.click(
                    button_info['rect']['x'] + button_info['rect']['width'] / 2,
                    button_info['rect']['y'] + button_info['rect']['height'] / 2
                )
            ]
            
            for i, strategy in enumerate(strategies):
                try:
                    await strategy()
                    logger.debug(f"Click strategy {i+1} succeeded")
                    
                    # Wait for navigation or state change
                    await asyncio.sleep(1)  # Brief pause
                    
                    # Check if we've moved to password state
                    has_password = await self.page.evaluate("""
                        () => document.querySelector('input[type="password"]') !== null
                    """)
                    
                    if has_password:
                        logger.debug("Successfully moved to password state")
                        return
                        
                except Exception as e:
                    logger.debug(f"Click strategy {i+1} failed: {e}")
                    continue
                    
            raise InteractionError(
                message="All click strategies failed",
                action="click_continue",
                details={'button_info': button_info}
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
            # Wait for password field
            await self.page.wait_for_selector(
                'input[type="password"]',
                state='visible',
                timeout=30000
            )
            
            # Fill using JavaScript
            await self.page.evaluate(f"""
                () => {{
                    const input = document.querySelector('input[type="password"]');
                    if (input) {{
                        input.value = "{password}";
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            """)
            
            logger.debug("Filled password field")
            
        except Exception as e:
            logger.error(f"Failed to fill password: {e}")
            raise InteractionError(
                message="Failed to fill password field",
                action="fill_password",
                details={'error': str(e)}
            )
            
    async def click_sign_in(self) -> None:
        """Click the sign in button."""
        try:
            # Wait for sign in button
            await self.page.wait_for_selector(
                '[data-testid="sign-in-button"]',
                state='visible',
                timeout=30000
            )
            
            # Click using JavaScript
            await self.page.evaluate("""
                () => {
                    const button = document.querySelector('[data-testid="sign-in-button"]');
                    if (button) {
                        button.click();
                    }
                }
            """)
            
            logger.debug("Clicked sign in button")
            
        except Exception as e:
            logger.error(f"Failed to click sign in: {e}")
            raise InteractionError(
                message="Failed to click sign in button",
                action="click_sign_in",
                details={'error': str(e)}
            )
            
    async def verify_login_success(self) -> bool:
        """Verify successful login."""
        try:
            await self.page.wait_for_selector(
                '[data-testid="dashboard-container"]',
                state='visible',
                timeout=30000
            )
            logger.info("Login successful - dashboard found")
            return True
        except Exception:
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