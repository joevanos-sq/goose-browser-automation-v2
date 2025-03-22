"""Web component handler with specific support for Square components."""
import logging
from typing import Optional, Dict, Any
from playwright.async_api import Page, ElementHandle
from ..utils.logging_utils import DebugLogger
from .exceptions import ElementNotFoundError, SquareComponentError

logger = DebugLogger().logger

class WebComponentHandler:
    """Handles interactions with web components, especially Square's custom elements."""
    
    SQUARE_SELECTORS = {
        'sign_in_button': [
            "market-button[data-testid='login-password-submit-button']",
            "market-button[name='sign-in-button']",
            ".split-login-password-view-actions market-button",
            "market-button[data-test-submit]"
        ],
        'continue_button': [
            "market-button[data-testid='login-email-submit-button']",
            "market-button[name='continue-button']"
        ],
        'email_input': [
            "market-input-text[data-testid='email-input']",
            "market-input-text[name='email']"
        ],
        'password_input': [
            "market-input-text[data-testid='password-input']",
            "market-input-text[name='password']"
        ]
    }
    
    def __init__(self, page: Page):
        """Initialize with Playwright page."""
        self.page = page
        
    async def find_button_by_text(self, text: str, timeout: int = 5000) -> Optional[ElementHandle]:
        """Find a button by its text content, with specific handling for Square buttons."""
        # Special handling for Sign in button
        if text.lower() == "sign in":
            for selector in self.SQUARE_SELECTORS['sign_in_button']:
                try:
                    logger.debug(f"Trying selector for Sign in button: {selector}")
                    element = await self.page.wait_for_selector(
                        selector,
                        timeout=timeout/len(self.SQUARE_SELECTORS['sign_in_button']),
                        state='visible'
                    )
                    if element:
                        logger.info(f"Found Sign in button using selector: {selector}")
                        return element
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
                    
        # Special handling for Continue button
        elif text.lower() == "continue":
            for selector in self.SQUARE_SELECTORS['continue_button']:
                try:
                    logger.debug(f"Trying selector for Continue button: {selector}")
                    element = await self.page.wait_for_selector(
                        selector,
                        timeout=timeout/len(self.SQUARE_SELECTORS['continue_button']),
                        state='visible'
                    )
                    if element:
                        logger.info(f"Found Continue button using selector: {selector}")
                        return element
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
                    
        # Generic button finding as fallback
        generic_selectors = [
            f"market-button:has-text('{text}')",
            f"market-button[name='{text.lower()}-button']",
            f"market-button[data-testid*='{text.lower()}']"
        ]
        
        for selector in generic_selectors:
            try:
                element = await self.page.wait_for_selector(
                    selector,
                    timeout=timeout/len(generic_selectors),
                    state='visible'
                )
                if element:
                    return element
            except Exception:
                continue
                
        return None

    async def click_button_safely(self, text: str) -> bool:
        """Safely click a button with enhanced error handling."""
        button = await self.find_button_by_text(text)
        if not button:
            logger.error(f"Could not find clickable button with text: {text}")
            return False
            
        try:
            # Ensure button is ready
            await button.wait_for_element_state('stable')
            
            # Scroll into view if needed
            await self.ensure_element_in_viewport(button)
            
            # Click with retry
            await self.retry_with_backoff(lambda: button.click())
            
            logger.info(f"Successfully clicked button: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click button '{text}': {str(e)}")
            await self.debug_button_state(button, text)
            return False
            
    async def ensure_element_in_viewport(self, element: ElementHandle):
        """Ensure element is in viewport for reliable interaction."""
        await self.page.evaluate("""element => {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center'
            });
        }""", element)
        
        # Wait for scroll to complete
        await self.page.wait_for_timeout(100)
        
    async def retry_with_backoff(self, action, max_retries: int = 3, initial_delay: int = 100):
        """Retry an action with exponential backoff."""
        last_error = None
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                return await action()
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}ms: {str(e)}"
                    )
                    await self.page.wait_for_timeout(delay)
                    delay *= 2
                    
        raise last_error
        
    async def debug_button_state(self, button: ElementHandle, text: str):
        """Debug button state and log details."""
        try:
            state = await button.evaluate("""button => ({
                visible: button.offsetParent !== null,
                enabled: !button.disabled,
                position: button.getBoundingClientRect(),
                styles: {
                    display: window.getComputedStyle(button).display,
                    visibility: window.getComputedStyle(button).visibility,
                    opacity: window.getComputedStyle(button).opacity
                },
                attributes: Object.fromEntries(
                    Array.from(button.attributes).map(attr => [attr.name, attr.value])
                ),
                text: button.textContent.trim()
            })""")
            
            logger.debug(f"Button state for '{text}': {json.dumps(state, indent=2)}")
            
        except Exception as e:
            logger.error(f"Failed to get button state: {str(e)}")

    async def find_input(self, identifier: str) -> Optional[ElementHandle]:
        """Find an input element using Square-specific selectors."""
        if identifier == "email":
            selectors = self.SQUARE_SELECTORS['email_input']
        elif identifier == "password":
            selectors = self.SQUARE_SELECTORS['password_input']
        else:
            selectors = [
                f"market-input-text[data-testid='{identifier}']",
                f"market-input-text[name='{identifier}']"
            ]
            
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(
                    selector,
                    state='visible'
                )
                if element:
                    return element
            except Exception:
                continue
                
        return None