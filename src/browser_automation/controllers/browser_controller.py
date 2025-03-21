"""Browser controller using Playwright."""
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, Playwright
import logging

logger = logging.getLogger(__name__)

class BrowserController:
    """Controls browser automation using Playwright."""
    
    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        
    @property
    def page(self) -> Optional[Page]:
        """Get current page."""
        return self._page
        
    async def launch(self, headless: bool = False) -> None:
        """Launch browser and create page."""
        try:
            # Clean up any existing instances
            await self.cleanup()
            
            logger.info("Starting Playwright...")
            self._playwright = await async_playwright().start()
            
            try:
                logger.info("Attempting to launch Chrome Canary...")
                self._browser = await self._playwright.chromium.launch(
                    channel="chrome-canary",
                    headless=headless,
                    args=['--start-maximized']  # Start with maximized window
                )
                logger.info("Successfully launched Chrome Canary")
            except Exception as e:
                logger.error(f"Failed to launch Chrome Canary: {str(e)}")
                logger.info("Attempting to fall back to regular Chrome...")
                self._browser = await self._playwright.chromium.launch(
                    headless=headless,
                    args=['--start-maximized']  # Start with maximized window
                )
                logger.info("Successfully launched regular Chrome")
                
            logger.info("Creating new page...")
            self._page = await self._browser.new_page()
            
            # Set viewport size
            await self._page.set_viewport_size({"width": 1920, "height": 1080})
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            await self.cleanup()
            raise McpError(
                ErrorData(INTERNAL_ERROR, f"Failed to launch browser: {str(e)}")
            )
            
    async def navigate(self, url: str) -> None:
        """Navigate to URL."""
        if not self._page:
            raise ValueError("Browser not launched")
            
        logger.info(f"Navigating to {url}")
        await self._page.goto(url)
        await self._page.wait_for_load_state("networkidle")
        
    async def inspect_page(self, selector: str = "body") -> Dict[str, Any]:
        """
        Inspect the current page content and structure.
        
        Args:
            selector: CSS selector to target specific elements
            
        Returns:
            Dictionary containing page content and metadata
        """
        if not self._page:
            raise ValueError("Browser not launched")
            
        # Wait for the selector to be available
        element = await self._page.wait_for_selector(selector)
        if not element:
            raise ValueError(f"Element not found: {selector}")
            
        # Get various types of content
        text_content = await element.text_content()
        inner_text = await element.inner_text()
        html = await element.inner_html()
        
        # Get page title and URL
        title = await self._page.title()
        url = self._page.url
        
        # Return structured content
        return {
            "title": title,
            "url": url,
            "text": text_content.strip(),
            "inner_text": inner_text.strip(),
            "html": html,
            "selector": selector
        }
        
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        if self._page:
            try:
                await self._page.close()
            except Exception as e:
                logger.warning(f"Error closing page: {e}")
            self._page = None
            
        if self._browser:
            try:
                await self._browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            self._browser = None
            
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
            self._playwright = None