"""Browser controller with Chromium support."""
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page, Browser, Playwright, BrowserContext
import logging
from .square_controller import SquareController

# Configure logging
logger = logging.getLogger(__name__)

class BrowserController:
    """Controls browser automation with Chromium."""
    
    def __init__(self):
        """Initialize the controller."""
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._square: Optional[SquareController] = None
        
    @property
    def page(self) -> Optional[Page]:
        """Get current page."""
        return self._page
        
    async def launch(self, headless: bool = True, viewport: Optional[Dict[str, int]] = None) -> bool:
        """
        Launch Chromium browser.
        
        Args:
            headless: Whether to run browser in headless mode
            viewport: Dictionary with 'width' and 'height' for viewport size
            
        Returns:
            bool: True if launch successful, False otherwise
        """
        try:
            self._playwright = await async_playwright().start()
            
            # Launch Chromium with specific options
            self._browser = await self._playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-dev-shm-usage',  # Helps with stability in Docker
                    '--no-sandbox',  # Required for running in certain environments
                    '--disable-setuid-sandbox',
                    '--disable-gpu',  # Reduces issues in headless mode
                    '--disable-software-rasterizer',
                ]
            )
            
            # Create a new context with viewport settings
            context_options = {
                'viewport': viewport or {'width': 1280, 'height': 720},
                'accept_downloads': True,
                'ignore_https_errors': True  # Useful for testing environments
            }
            
            self._context = await self._browser.new_context(**context_options)
            self._page = await self._context.new_page()
            
            # Initialize Square controller
            self._square = SquareController(self._page)
            
            # Enable request/response logging
            await self._setup_network_logging()
            
            logger.info("Chromium browser launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            return False
            
    async def _setup_network_logging(self) -> None:
        """Setup network request/response logging."""
        if not self._page:
            return
            
        async def log_request(request):
            logger.debug(f"Request: {request.method} {request.url}")
            
        async def log_response(response):
            logger.debug(f"Response: {response.status} {response.url}")
            
        self._page.on('request', log_request)
        self._page.on('response', log_response)
        
    async def navigate(self, url: str, wait_until: str = 'networkidle', timeout: int = 30000) -> bool:
        """
        Navigate to URL with advanced error handling.
        
        Args:
            url: URL to navigate to
            wait_until: Navigation wait condition ('networkidle', 'load', 'domcontentloaded')
            timeout: Navigation timeout in milliseconds
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if not self._page:
            logger.error("No page available")
            return False
            
        try:
            response = await self._page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout
            )
            
            if not response or not response.ok:
                logger.error(f"Navigation to {url} failed with status {response.status if response else 'no response'}")
                return False
                
            await self._page.wait_for_load_state('networkidle')
            logger.info(f"Successfully navigated to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
            
    async def get_page_state(self) -> Dict[str, Any]:
        """Get current page state for debugging."""
        if not self._page or not self._context:
            return {}
            
        try:
            viewport_size = await self._page.viewport_size() or {'width': 0, 'height': 0}
            return {
                'url': self._page.url,
                'title': await self._page.title(),
                'content_size': len(await self._page.content()),
                'viewport': viewport_size,
                'cookies': await self._context.cookies()
            }
        except Exception as e:
            logger.error(f"Failed to get page state: {str(e)}")
            return {}
            
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            
    def get_square_controller(self) -> Optional[SquareController]:
        """Get Square controller instance."""
        return self._square