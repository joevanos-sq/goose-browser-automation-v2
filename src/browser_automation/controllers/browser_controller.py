"""Browser controller with Chromium support."""
from __future__ import annotations

import logging
import time
from typing import Dict, Any, Optional, Literal, List, cast
from playwright.async_api import async_playwright, Page, Browser, Playwright, Locator
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

    def _ensure_page(self) -> Page:
        """Ensure page exists and return it typed correctly."""
        if not self._page:
            raise ValueError("Browser not launched")
        return cast(Page, self._page)

    async def launch(self, headless: bool = False) -> bool:
        """Launch browser with optimized settings."""
        try:
            start_time = time.time()
            
            self._playwright = await async_playwright().start()
            
            # Launch with minimal options
            self._browser = await self._playwright.chromium.launch(
                channel="chrome-canary",
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins',
                ]
            )
            
            # Create page with minimal settings
            self._page = await self._browser.new_page()
            
            # Block image loading but allow CSS for layout
            await self._page.route("**/*.{png,jpg,jpeg,svg,gif}", lambda route: route.abort())
            await self._page.route("**/*.css", lambda route: route.continue_())
            
            logger.info(f"Browser launch took {(time.time() - start_time) * 1000:.0f}ms")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            return False

    async def navigate(self, url: str, wait_for: Literal['load', 'domcontentloaded', 'networkidle'] = 'load') -> bool:
        """Navigate to URL with smart navigation optimizations."""
        try:
            page = self._ensure_page()
            start_time = time.time()
            
            # Smart navigation: Check if we're already on the page
            current_url = page.url
            logger.info(f"Current URL: {current_url}")
            logger.info(f"Target URL: {url}")
            
            # Strip hash/query params for base URL comparison
            current_base = current_url.split('#')[0].split('?')[0]
            target_base = url.split('#')[0].split('?')[0]
            
            if current_url == url:
                logger.info("✨ Smart Navigation: Already on requested URL, skipping navigation")
                return True
                
            if current_base == target_base:
                # Same page, different anchor/params - use client-side navigation
                logger.info("✨ Smart Navigation: Using client-side navigation")
                if '#' in url:
                    anchor = url.split('#')[1]
                    logger.info(f"Updating hash to: #{anchor}")
                    await page.evaluate(f"window.location.hash = '{anchor}'")
                elif '?' in url:
                    query = url.split('?')[1]
                    logger.info(f"Updating query to: ?{query}")
                    await page.evaluate(f"window.location.search = '{query}'")
                await page.wait_for_timeout(100)  # Brief delay for client-side update
                logger.info(f"✨ Client-side navigation completed in {(time.time() - start_time) * 1000:.0f}ms")
                return True
            
            # Full navigation needed
            logger.info("Performing full page navigation")
            await page.goto(url, wait_until='commit', timeout=5000)
            
            # Set viewport size asynchronously
            viewport_task = page.set_viewport_size({"width": 1280, "height": 800})
            
            # Wait for critical content
            content_task = page.wait_for_load_state(wait_for, timeout=5000)
            
            # Run tasks concurrently
            await viewport_task
            await content_task
            
            logger.info(f"Full navigation completed in {(time.time() - start_time) * 1000:.0f}ms")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False

    async def click_with_retry(self, selector: str, max_attempts: int = 2, delay: int = 50, ensure_visible: bool = True) -> bool:
        """
        Click element with minimal retry.
        
        Args:
            selector: Element selector to click
            max_attempts: Maximum number of retry attempts
            delay: Delay between retries in milliseconds
            ensure_visible: Whether to ensure element is visible before clicking
            
        Returns:
            bool: True if click successful, False otherwise
        """
        page = self._ensure_page()
        start_time = time.time()
        
        try:
            # Get the element using locator
            element = page.locator(selector)
            
            # Try immediate click first
            try:
                if ensure_visible:
                    await element.scroll_into_view_if_needed()
                await element.click(timeout=1000)
                logger.info(f"Click succeeded immediately in {(time.time() - start_time) * 1000:.0f}ms")
                return True
            except:
                pass  # Try retry logic if immediate click fails
            
            # Retry logic with minimal delay
            for attempt in range(max_attempts):
                try:
                    await element.wait_for(state='visible', timeout=1000)
                    if ensure_visible:
                        await element.scroll_into_view_if_needed()
                    await element.click(timeout=1000)
                    logger.info(f"Click succeeded on attempt {attempt + 1} in {(time.time() - start_time) * 1000:.0f}ms")
                    return True
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Click failed after {max_attempts} attempts: {str(e)}")
                        return False
                    await page.wait_for_timeout(delay)
            
            return False
            
        except Exception as e:
            logger.error(f"Click operation failed: {str(e)}")
            return False

    async def click_element(self, selector: str, ensure_visible: bool = True) -> bool:
        """Click on an element."""
        return await self.click_with_retry(selector, ensure_visible=ensure_visible)

    async def type_text(self, selector: str, text: str, submit: bool = False) -> bool:
        """Type text into an element with optional submit."""
        page = self._ensure_page()
        try:
            element = page.locator(selector)
            await element.fill(text)
            if submit:
                await element.press('Enter')
                await page.wait_for_load_state('networkidle')
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            return False

    async def inspect_page(self, 
                         selector: str = "body",
                         max_elements: int = 100,
                         element_types: Optional[List[str]] = None,
                         attributes: Optional[List[str]] = None,
                         max_depth: int = 3,
                         mode: Literal['all', 'clickable', 'form'] = 'all') -> Dict[str, Any]:
        """Get page state with configurable inspection options."""
        page = self._ensure_page()
        inspector = ElementInspector(page)
        try:
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
            logger.error(f"Page inspection failed: {str(e)}")
            return {"error": str(e)}

    async def click_result_by_text(self, text: str, ensure_visible: bool = True, allowed_types: List[str] = ['organic']) -> bool:
        """
        Click result containing specified text.
        
        Args:
            text: Text to match in result
            ensure_visible: Whether to ensure result is visible
            allowed_types: List of allowed result types (default: ['organic'])
            
        Returns:
            bool: True if click successful, False otherwise
        """
        page = self._ensure_page()
        smart_selector = SmartSelector(page)
        try:
            element = await smart_selector.find_element(
                target_text=text,
                element_type="link",
                context="search-results",
                attributes=["href", "class", "role"]
            )
            if not element:
                logger.error(f"Could not find result containing text: {text}")
                return False
            
            if ensure_visible:
                await element.scroll_into_view_if_needed()
            await element.click()
            return True
        except Exception as e:
            logger.error(f"Failed to click result: {str(e)}")
            return False

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            start_time = time.time()
            
            if self._page:
                await self._page.close()
                self._page = None
                
            if self._browser:
                await self._browser.close()
                self._browser = None
                
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                
            logger.info(f"Browser cleanup took {(time.time() - start_time) * 1000:.0f}ms")
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            raise