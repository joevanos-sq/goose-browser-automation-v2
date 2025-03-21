"""Browser controller using Playwright."""
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, Playwright, Route, Request
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR
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
        
    async def handle_route(self, route: Route, request: Request) -> None:
        """Handle route interception."""
        if request.resource_type == "image":
            await route.abort()
        else:
            await route.continue_()
            
    async def launch(self, headless: bool = False) -> None:
        """Launch browser and create page."""
        try:
            # Clean up any existing instances
            await self.cleanup()
            
            logger.info("Starting Playwright...")
            self._playwright = await async_playwright().start()
            
            try:
                logger.info("Launching Chrome Canary...")
                self._browser = await self._playwright.chromium.launch(
                    channel="chrome-canary",
                    headless=headless,
                    args=[
                        '--start-maximized',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials'
                    ]
                )
                logger.info("Successfully launched Chrome Canary")
            except Exception as e:
                logger.error(f"Failed to launch Chrome Canary: {str(e)}")
                logger.info("Attempting to fall back to regular Chrome...")
                self._browser = await self._playwright.chromium.launch(
                    headless=headless,
                    args=[
                        '--start-maximized',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials'
                    ]
                )
                logger.info("Successfully launched regular Chrome")
                
            logger.info("Creating new page...")
            context = await self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
                ignore_https_errors=True,
                bypass_csp=True,
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            # Set cookie consent
            await context.add_cookies([{
                'name': 'OptanonAlertBoxClosed',
                'value': '2024-03-21T21:37:48.853Z',
                'domain': '.squareupstaging.com',
                'path': '/'
            }])
            
            self._page = await context.new_page()
            
            # Route handling for better performance
            await self._page.route("**/*", self.handle_route)
            
            # Enable better logging
            self._page.on('console', lambda msg: logger.debug(f'Browser console {msg.type}: {msg.text}'))
            self._page.on('pageerror', lambda err: logger.error(f'Browser page error: {err}'))
            
            # Set default navigation timeout
            self._page.set_default_navigation_timeout(60000)
            self._page.set_default_timeout(30000)
            
            # Wait for JavaScript to be ready
            await self._page.evaluate("() => window.innerWidth")
            
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
        
        try:
            # Navigate with longer timeout and wait until network is idle
            response = await self._page.goto(
                url,
                wait_until='networkidle',
                timeout=60000
            )
            
            if not response:
                raise ValueError(f"Failed to get response from {url}")
                
            if not response.ok:
                raise ValueError(f"Got {response.status} response from {url}")
                
            # Wait for critical states
            await self._page.wait_for_load_state('domcontentloaded')
            await self._page.wait_for_load_state('networkidle')
            
            # Ensure JavaScript is working
            is_js_working = await self._page.evaluate("""() => {
                return typeof window.jQuery !== 'undefined' || 
                       typeof window.React !== 'undefined' ||
                       document.readyState === 'complete';
            }""")
            
            if not is_js_working:
                raise ValueError("JavaScript is not properly initialized")
                
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            raise
        
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
            
        try:
            # Wait for the selector to be available
            element = await self._page.wait_for_selector(selector, state='visible')
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
        except Exception as e:
            logger.error(f"Page inspection failed: {str(e)}")
            raise
        
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