"""Browser controller with Chromium support."""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Literal
from playwright.async_api import async_playwright, Page, Browser, Playwright

logger = logging.getLogger(__name__)

class BrowserController:
    """Controls browser automation with Chromium."""
    
    def __init__(self) -> None:
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
            
        Returns:
            bool: True if launch successful, False otherwise
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
            
        Returns:
            bool: True if navigation successful, False otherwise
            
        Raises:
            ValueError: If browser not launched
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            await self._page.goto(
                url,
                wait_until='networkidle'  # Using literal value
            )
            logger.info(f"Successfully navigated to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
            
    async def type_text(self, selector: str, text: str) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: Element selector or name
            text: Text to type
            
        Returns:
            bool: True if text entered successfully, False otherwise
            
        Raises:
            ValueError: If browser not launched
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            # Try by role
            element = self._page.get_by_role('textbox', name=selector)
            if element:
                await element.fill(text)
                await element.press('Enter')
                logger.info(f"Successfully typed text into {selector}")
                return True
                
            # Try by placeholder
            element = self._page.get_by_placeholder(selector)
            if element:
                await element.fill(text)
                await element.press('Enter')
                return True
                
            # Try direct selector
            element = self._page.locator(selector)
            await element.fill(text)
            await element.press('Enter')
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            return False
            
    async def click_element(self, selector: str) -> bool:
        """
        Click on an element.
        
        Args:
            selector: Element selector or name
            
        Returns:
            bool: True if click successful, False otherwise
            
        Raises:
            ValueError: If browser not launched
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            # Try by role
            element = self._page.get_by_role('link', name=selector)
            if element:
                await element.click()
                logger.info(f"Successfully clicked {selector}")
                return True
                
            # Try by text
            element = self._page.get_by_text(selector)
            if element:
                await element.click()
                return True
                
            # Try direct selector
            element = self._page.locator(selector)
            await element.click()
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element: {str(e)}")
            return False
            
    async def inspect_page(self, selector: str = "body") -> Dict[str, Any]:
        """
        Get current page state for debugging.
        
        Args:
            selector: Element selector to inspect
            
        Returns:
            Dict containing page state information
            
        Raises:
            ValueError: If browser not launched
        """
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
        """
        Close browser and cleanup resources.
        
        Raises:
            Exception: If cleanup fails
        """
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