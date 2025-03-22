"""Browser controller with Chromium support."""
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser, Playwright

logger = logging.getLogger(__name__)

class BrowserController:
    """Controls browser automation with Chromium."""
    
    def __init__(self):
        """Initialize the controller."""
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        
    @property
    def page(self) -> Optional[Page]:
        """Get current page."""
        return self._page
        
    async def launch(self, headless: bool = False) -> bool:
        """
        Launch Chromium browser.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        try:
            self._playwright = await async_playwright().start()
            
            # Launch Chromium with specific options
            self._browser = await self._playwright.chromium.launch(
                channel="chrome-canary",
                headless=headless
            )
            
            self._page = await self._browser.new_page()
            logger.info("Browser launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            return False
            
    async def navigate(self, url: str) -> bool:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            await self._page.goto(url)
            await self._page.wait_for_load_state('networkidle')
            logger.info(f"Successfully navigated to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
            
    async def inspect_page(self, selector: str = "body") -> Dict[str, Any]:
        """Get current page state for debugging."""
        if not self._page:
            raise ValueError("Browser not launched")
            
        try:
            element = await self._page.query_selector(selector)
            if not element:
                return {"error": f"Element not found: {selector}"}
                
            content = await element.inner_html()
            return {
                "url": self._page.url,
                "title": await self._page.title(),
                "content": content
            }
        except Exception as e:
            logger.error(f"Failed to inspect page: {str(e)}")
            return {"error": str(e)}
            
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self._page:
                await self._page.close()
                self._page = None
                
            if self._browser:
                await self._browser.close()
                self._browser = None
                
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            raise