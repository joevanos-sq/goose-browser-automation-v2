"""Square-specific automation controller."""
import logging
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class SquareController:
    """Controls Square-specific automation tasks."""
    
    def __init__(self, page: Page):
        self.page = page
        
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
            # Navigate to login page
            logger.info("Navigating to Square login page...")
            await self.page.goto('https://app.squareupstaging.com/login')
            await self.page.wait_for_load_state("networkidle")
            
            # Fill email
            logger.info("Entering email...")
            email_input = self.page.get_by_role('textbox', name='Email or phone number')
            await email_input.fill(email)
            
            # Click continue
            logger.info("Clicking continue...")
            continue_button = self.page.get_by_role('button', name='Continue')
            await continue_button.click()
            
            # Wait for password field
            await self.page.wait_for_load_state("networkidle")
            
            # Fill password
            logger.info("Entering password...")
            password_input = self.page.get_by_role('textbox', name='Password')
            await password_input.fill(password)
            
            # Click sign in
            logger.info("Clicking sign in...")
            sign_in_button = self.page.get_by_role('button', name='Sign in')
            await sign_in_button.click()
            
            # Wait for navigation and verify login
            await self.page.wait_for_load_state("networkidle")
            
            # Check if we're logged in by looking for common dashboard elements
            try:
                await self.page.wait_for_selector('[data-testid="dashboard-container"]', timeout=5000)
                logger.info("Login successful")
                return True
            except Exception as e:
                logger.error(f"Login verification failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False