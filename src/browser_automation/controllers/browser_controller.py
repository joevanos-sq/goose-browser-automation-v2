"""Browser automation controller."""
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser, Playwright
from .square_controller_new import SquareController

logger = logging.getLogger(__name__)


class BrowserController:
    """Controls browser automation."""
    
    def __init__(self):
        """Initialize the controller."""
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._square: Optional[SquareController] = None
        
    async def launch(self) -> bool:
        """Launch the browser."""
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True
            )
            self._page = await self._browser.new_page()
            self._square = SquareController(self._page)
            logger.info("Browser launched successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return False
            
    async def close(self) -> None:
        """Close the browser."""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")
            
    async def square_login(self, email: str, password: str) -> bool:
        """Handle Square login."""
        if not self._square:
            logger.error("Square controller not initialized")
            return False
            
        return await self._square.login(email, password)