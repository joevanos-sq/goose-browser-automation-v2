"""Browser controller with Chromium support."""
from __future__ import annotations

import logging
import random
from typing import Dict, Any, Optional, Literal, List
from playwright.async_api import async_playwright, Page, Browser, Playwright
from browser_automation.utils.selectors import GoogleSelectors
from browser_automation.utils.inspector import ElementInspector
from browser_automation.utils.smart_selector import SmartSelector

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
            # Launch with anti-detection measures
            self._browser = await self._playwright.chromium.launch(
                channel="chrome-canary",
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                ]
            )
            
            self._page = await self._browser.new_page()
            logger.info("Browser launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            return False
            
    async def navigate(self, url: str, wait_for: Literal['load', 'domcontentloaded', 'networkidle'] = 'networkidle') -> bool:
        """
        Navigate to URL and wait for specified state.
        
        Args:
            url: URL to navigate to
            wait_for: State to wait for after navigation
            
        Returns:
            bool: True if navigation successful, False otherwise
            
        Raises:
            ValueError: If browser not launched
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            # Set human-like viewport and window size
            await self._page.set_viewport_size({"width": 1280, "height": 800})
            
            # Add human-like headers
            await self._page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Upgrade-Insecure-Requests": "1"
            })
            
            # Navigate with a more natural timing
            await self._page.goto(url, wait_until=wait_for, timeout=30000)
            await self._page.wait_for_load_state(wait_for)
            
            # Add a small random delay to simulate human behavior
            await self._page.wait_for_timeout(1000 + (random.random() * 1000))
            
            logger.info(f"Successfully navigated to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False

    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        """
        Wait for element to be visible and ready.
        
        Args:
            selector: Element selector
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            bool: True if element found, False if timeout
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            await self._page.wait_for_selector(selector, 
                state='visible',
                timeout=timeout
            )
            return True
        except Exception as e:
            logger.error(f"Wait for element failed: {str(e)}")
            return False
            
    async def type_text(self, selector: str, text: str, submit: bool = False) -> bool:
        """
        Type text into an element with optional submit.
        
        Args:
            selector: Element selector
            text: Text to type
            submit: Whether to press Enter after typing
            
        Returns:
            bool: True if text entered successfully, False otherwise
            
        Raises:
            ValueError: If browser not launched
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")

            # Wait for element to be ready    
            await self.wait_for_element(selector)
            
            # Type the text
            element = self._page.locator(selector)
            await element.fill(text)
            
            if submit:
                await element.press('Enter')
                # Wait for navigation if submitting
                await self._page.wait_for_load_state('networkidle')
                
            logger.info(f"Successfully typed text into {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            return False
            
    async def click_element(self, selector: str, ensure_visible: bool = True) -> bool:
        """
        Click on an element with improved reliability.
        
        Args:
            selector: Element selector
            ensure_visible: Whether to ensure element is in viewport
            
        Returns:
            bool: True if click successful, False otherwise
            
        Raises:
            ValueError: If browser not launched
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            # Wait for element first
            await self.wait_for_element(selector)
            
            # Get the element
            element = self._page.locator(selector)
            
            # Ensure element is in viewport if requested
            if ensure_visible:
                await element.scroll_into_view_if_needed()
                await self._page.wait_for_timeout(500)  # Small delay after scroll
                
            # Click the element
            await element.click()
            logger.info(f"Successfully clicked {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element: {str(e)}")
            return False

    async def wait_for_search_results(self, timeout: int = 5000) -> bool:
        """
        Wait for Google search results to be visible and interactive.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            bool: True if results are ready, False otherwise
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            # Wait for main results container
            await self.wait_for_element(GoogleSelectors.SEARCH['search_results'], timeout)
            
            # Wait for at least one organic result
            await self.wait_for_element(GoogleSelectors.SEARCH['organic_results'], timeout)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed waiting for search results: {str(e)}")
            return False
            
    async def get_result_count(self) -> int:
        """
        Get number of search results on current page.
        
        Returns:
            int: Number of results found
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            results = await self._page.query_selector_all(GoogleSelectors.SEARCH['organic_results'])
            return len(results)
            
        except Exception as e:
            logger.error(f"Failed to get result count: {str(e)}")
            return 0
            
    async def get_result_texts(self) -> List[str]:
        """
        Get list of result titles on current page.
        
        Returns:
            List[str]: List of result titles
        """
        try:
            if not self._page:
                raise ValueError("Browser not launched")
                
            titles = []
            elements = await self._page.query_selector_all(GoogleSelectors.SEARCH['result_titles'])
            
            for element in elements:
                title = await element.inner_text()
                titles.append(title)
                
            return titles
            
        except Exception as e:
            logger.error(f"Failed to get result texts: {str(e)}")
            return []
            
    async def click_result_by_index(self, index: int, ensure_visible: bool = True) -> bool:
        """
        Click search result by position (1-based index).
        
        Args:
            index: Position of result to click (1-based)
            ensure_visible: Whether to ensure result is in viewport
            
        Returns:
            bool: True if click successful, False otherwise
        """
        selector = GoogleSelectors.get_result_by_index(index)
        return await self.click_element(selector, ensure_visible)
        
    async def click_result_by_text(self, text: str, ensure_visible: bool = True) -> bool:
        """
        Click search result containing specified text using smart selection.
        
        Args:
            text: Text to match in result title
            ensure_visible: Whether to ensure result is in viewport
            
        Returns:
            bool: True if click successful, False otherwise
        """
        if not self._page:
            raise ValueError("Browser not launched")
            
        smart_selector = SmartSelector(self._page)
        element = await smart_selector.find_element(
            target_text=text,
            element_type="link",
            context="search-results"
        )
        
        if not element:
            logger.error(f"Could not find result containing text: {text}")
            return False
            
        try:
            if ensure_visible:
                await element.scroll_into_view_if_needed()
                await self._page.wait_for_timeout(500)  # Small delay after scroll
                
            await element.click()
            logger.info(f"Successfully clicked result containing: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click result: {str(e)}")
            return False
            
    async def inspect_page(self, 
                      selector: str = "body",
                      max_elements: int = 100,
                      element_types: Optional[List[str]] = None,
                      attributes: Optional[List[str]] = None,
                      max_depth: int = 3,
                      mode: Literal['all', 'clickable', 'form'] = 'all') -> Dict[str, Any]:
        """
        Get current page state with configurable inspection options.
        
        Args:
            selector: Element selector to inspect
            max_elements: Maximum number of elements to return
            element_types: List of element types to include (e.g. ['a', 'button'])
            attributes: List of attributes to include in results
            max_depth: Maximum depth to traverse in DOM tree
            mode: Inspection mode - 'all' for full tree, 'clickable' for interactive elements,
                 or 'form' for form elements
            
        Returns:
            Dict containing filtered page state information
            
        Raises:
            ValueError: If browser not launched
        """
        if not self._page:
            raise ValueError("Browser not launched")
            
        try:
            inspector = ElementInspector(self._page)
            
            if mode == 'clickable':
                return await inspector.find_clickable_elements(max_elements)
            elif mode == 'form':
                return await inspector.find_form_elements(max_elements)
            else:
                return await inspector.inspect_page(
                    selector=selector,
                    max_elements=max_elements,
                    element_types=element_types,
                    attributes=attributes,
                    max_depth=max_depth
                )
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