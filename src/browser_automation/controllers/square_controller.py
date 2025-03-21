"""Square-specific automation controller."""
import logging
import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import Page, TimeoutError
from ..square_selectors import SquareSelectors, SquareConfig
from ..utils.enhanced_inspector import EnhancedInspector

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SquareController:
    """Controls Square-specific automation tasks."""
    
    def __init__(self, page: Page):
        self.page = page
        self.inspector = EnhancedInspector(page)
        self.debug_dir = Path(os.path.expanduser("~/.goose/debug"))
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_debug_screenshot(self, name: str):
        """Save a screenshot for debugging."""
        timestamp = asyncio.get_event_loop().time()
        path = self.debug_dir / f"{name}_{timestamp}.png"
        await self.page.screenshot(path=str(path))
        logger.debug(f"Saved screenshot to {path}")
        
    async def save_debug_info(self, name: str, data: dict):
        """Save debug information to a file."""
        timestamp = asyncio.get_event_loop().time()
        path = self.debug_dir / f"{name}_{timestamp}.json"
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved debug info to {path}")
        
    async def handle_cookie_consent(self):
        """Handle cookie consent banner."""
        try:
            # Check for OneTrust banner
            accept_button = self.page.locator('#accept-recommended-btn-handler')
            if await accept_button.is_visible():
                await accept_button.click()
                await self.page.wait_for_selector('#onetrust-banner-sdk', state='hidden')
                
        except Exception as e:
            logger.error(f"Error handling cookie consent: {str(e)}")
            
    async def wait_for_web_components(self):
        """Wait for web components to be defined."""
        await self.page.wait_for_function("""() => {
            return typeof customElements !== 'undefined' &&
                   customElements.get('market-button') !== undefined &&
                   customElements.get('market-input-text') !== undefined;
        }""")
        
    async def find_continue_button(self):
        """Find the continue button using multiple strategies."""
        logger.info("Looking for continue button...")
        
        # Get all clickable elements
        clickable = await self.inspector.find_clickable_elements()
        await self.save_debug_info("clickable_elements", clickable)
        logger.debug(f"Found {len(clickable)} clickable elements")
        
        # Log each clickable element
        for i, element in enumerate(clickable):
            logger.debug(f"Clickable element {i}:")
            logger.debug(f"  Tag: {element.get('tagName')}")
            logger.debug(f"  Text: {element.get('textContent')}")
            logger.debug(f"  Attributes: {element.get('attributes')}")
        
        # Inspect web components
        components = await self.inspector.inspect_web_components()
        await self.save_debug_info("web_components", components)
        logger.debug(f"Found web components: {list(components.keys())}")
        
        # Try different selectors
        selectors = [
            'market-button[data-testid="login-email-next-button"]',
            'button[data-testid="login-email-next-button"]',
            '[data-test-next]',
            'market-button[data-test-next]',
            'button:has-text("Continue")',
            'market-button:has-text("Continue")',
            '[role="button"]:has-text("Continue")'
        ]
        
        for selector in selectors:
            logger.debug(f"Trying selector: {selector}")
            element = await self.inspector.inspect_element(selector)
            if element:
                logger.debug(f"Found element with selector {selector}:")
                logger.debug(f"  Tag: {element.get('tagName')}")
                logger.debug(f"  Text: {element.get('textContent')}")
                logger.debug(f"  Attributes: {element.get('attributes')}")
                await self.save_debug_info(f"button_{selector.replace('[', '_').replace(']', '_')}", element)
                return selector
                
        return None
        
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
            await self.page.goto('https://app.squareupstaging.com/login', wait_until='networkidle')
            await self.save_debug_screenshot("01_initial_page")
            
            # Handle cookie consent
            logger.info("Handling cookie consent...")
            await self.handle_cookie_consent()
            
            # Wait for web components
            logger.info("Waiting for web components...")
            await self.wait_for_web_components()
            
            # Inspect initial page state
            logger.info("Inspecting initial page state...")
            components = await self.inspector.inspect_web_components()
            await self.save_debug_info("initial_components", components)
            
            # Wait for form to be ready
            logger.info("Waiting for login form...")
            await self.page.wait_for_selector('[data-testid="login-form-wrapper"]')
            
            # Fill email using JavaScript
            logger.info("Entering email...")
            await self.page.evaluate(f"""() => {{
                const input = document.querySelector('#mpui-combo-field-input');
                if (input) {{
                    input.value = "{email}";
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}""")
            await self.save_debug_screenshot("02_email_entered")
            
            # Find continue button
            logger.info("Finding continue button...")
            button_selector = await self.find_continue_button()
            if not button_selector:
                logger.error("Could not find continue button")
                return False
                
            # Inspect button before clicking
            logger.info("Inspecting continue button...")
            button_info = await self.inspector.inspect_element(button_selector)
            await self.save_debug_info("continue_button", button_info)
            
            # Try multiple click strategies
            logger.info("Trying multiple click strategies...")
            
            # 1. Try Playwright's built-in click
            try:
                logger.debug("Trying Playwright click...")
                button = self.page.locator(button_selector)
                await button.click(timeout=5000)
                logger.debug("Playwright click succeeded")
            except Exception as e:
                logger.debug(f"Playwright click failed: {str(e)}")
                
                # 2. Try JavaScript click
                try:
                    logger.debug("Trying JavaScript click...")
                    await self.page.evaluate(f"""(selector) => {{
                        const button = document.querySelector(selector);
                        if (button) {{
                            button.click();
                        }}
                    }}, "{button_selector}")""")
                    logger.debug("JavaScript click succeeded")
                except Exception as e:
                    logger.debug(f"JavaScript click failed: {str(e)}")
                    
                    # 3. Try dispatch click event
                    try:
                        logger.debug("Trying click event dispatch...")
                        await self.page.evaluate(f"""(selector) => {{
                            const button = document.querySelector(selector);
                            if (button) {{
                                const event = new MouseEvent('click', {{
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                }});
                                button.dispatchEvent(event);
                            }}
                        }}, "{button_selector}")""")
                        logger.debug("Click event dispatch succeeded")
                    except Exception as e:
                        logger.debug(f"Click event dispatch failed: {str(e)}")
                        return False
            
            # Wait for navigation
            await self.page.wait_for_load_state('networkidle')
            await self.save_debug_screenshot("03_after_continue")
            
            # Wait for password field using JavaScript polling
            logger.info("Waiting for password field...")
            await self.page.wait_for_function("""() => {
                return document.querySelector('input[type="password"]') !== null;
            }""")
            
            # Fill password using JavaScript
            logger.info("Entering password...")
            await self.page.evaluate(f"""() => {{
                const input = document.querySelector('input[type="password"]');
                if (input) {{
                    input.value = "{password}";
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}""")
            await self.save_debug_screenshot("04_password_entered")
            
            # Click sign in using JavaScript
            logger.info("Clicking sign in...")
            await self.page.evaluate("""() => {
                const button = document.querySelector('market-button[data-testid="sign-in-button"]');
                if (button) {
                    button.click();
                }
            }""")
            
            # Wait for navigation
            await self.page.wait_for_load_state('networkidle')
            await self.save_debug_screenshot("05_after_signin")
            
            # Check if we're logged in
            try:
                await self.page.wait_for_selector('[data-testid="dashboard-container"]')
                logger.info("Login successful")
                await self.save_debug_screenshot("06_login_success")
                return True
            except TimeoutError:
                logger.error("Login verification failed - dashboard not found")
                await self.save_debug_screenshot("06_login_failed")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            await self.save_debug_screenshot("error")
            return False