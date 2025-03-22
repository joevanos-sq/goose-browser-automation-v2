"""Square login controller."""
from __future__ import annotations

import logging
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class SquareController:
    """Controls Square-specific browser automation."""
    
    def __init__(self, page: Page) -> None:
        """
        Initialize with Playwright page.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        
    async def login(self, email: str, password: str) -> bool:
        """
        Execute Square login flow.
        
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
            
            # Wait for navigation
            await self.page.wait_for_load_state('networkidle')
            
            # Verify login success
            if await self._verify_login():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
            
    async def _verify_login(self) -> bool:
        """
        Verify successful login.
        
        Returns:
            bool: True if login verified, False otherwise
        """
        try:
            # Wait for URL change
            await self.page.wait_for_url(
                "**/dashboard**",
                timeout=5000
            )
            return True
        except Exception:
            return False