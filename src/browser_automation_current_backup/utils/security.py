"""Security utilities for browser automation."""
import logging
from typing import Optional, Dict, Any
from playwright.async_api import Page, Response

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utilities for handling security-related tasks."""
    
    def __init__(self, page: Page):
        self.page = page
        
    async def setup_request_interception(self):
        """Setup request interception for security headers."""
        await self.page.route("**/*", self._handle_request)
        
    async def _handle_request(self, route, request):
        """Handle intercepted requests."""
        # Add security headers
        headers = {
            **request.headers,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Continue with modified headers
        await route.continue_(headers=headers)
        
    async def bypass_recaptcha(self) -> bool:
        """
        Bypass reCAPTCHA by injecting a successful token.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if reCAPTCHA is present
            has_recaptcha = await self.page.evaluate("""() => {
                return document.querySelector('.grecaptcha-badge') !== null;
            }""")
            
            if not has_recaptcha:
                return True
                
            # Inject successful token
            await self.page.evaluate("""() => {
                window.___grecaptcha_cfg = {
                    clients: {
                        '0': {
                            eJ: () => {}
                        }
                    }
                };
                
                window.grecaptcha = {
                    enterprise: {
                        ready: (callback) => callback(),
                        execute: async (sitekey, options) => {
                            return 'mocked_token_for_testing';
                        }
                    }
                };
            }""")
            
            return True
            
        except Exception as e:
            logger.error(f"Error bypassing reCAPTCHA: {str(e)}")
            return False
            
    async def handle_cookie_consent(self) -> bool:
        """
        Handle cookie consent banner if present.
        
        Returns:
            bool: True if handled or not present, False if failed to handle
        """
        try:
            # Check for OneTrust banner
            has_banner = await self.page.evaluate("""() => {
                return document.querySelector('#onetrust-banner-sdk') !== null;
            }""")
            
            if not has_banner:
                return True
                
            # Accept cookies
            await self.page.evaluate("""() => {
                const acceptBtn = document.querySelector('#accept-recommended-btn-handler');
                if (acceptBtn) acceptBtn.click();
            }""")
            
            # Wait for banner to disappear
            await self.page.wait_for_function("""() => {
                return document.querySelector('#onetrust-banner-sdk') === null;
            }""")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling cookie consent: {str(e)}")
            return False
            
    async def setup_security_headers(self):
        """Setup common security headers."""
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        })
        
    async def bypass_security_checks(self) -> bool:
        """
        Bypass common security checks.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Inject security bypass
            await self.page.evaluate("""() => {
                // Bypass bot detection
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                
                // Bypass iframe security
                Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                    get: function() {
                        return window;
                    }
                });
                
                // Mock security-related APIs
                window.navigator.permissions = {
                    query: async () => ({
                        state: 'granted',
                        onchange: null
                    })
                };
                
                // Bypass CloudFlare checks
                window.navigator.chrome = {
                    runtime: {}
                };
            }""")
            
            return True
            
        except Exception as e:
            logger.error(f"Error bypassing security checks: {str(e)}")
            return False
            
    async def wait_for_navigation_with_security(self, url: str) -> Optional[Response]:
        """
        Navigate to URL with security handling.
        
        Args:
            url: URL to navigate to
            
        Returns:
            Response object if successful, None otherwise
        """
        try:
            # Setup security
            await self.setup_security_headers()
            await self.bypass_security_checks()
            
            # Navigate to page
            response = await self.page.goto(
                url,
                wait_until='networkidle',
                timeout=60000
            )
            
            if not response:
                return None
                
            # Handle security challenges
            await self.handle_cookie_consent()
            await self.bypass_recaptcha()
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state('domcontentloaded')
            await self.page.wait_for_load_state('networkidle')
            
            return response
            
        except Exception as e:
            logger.error(f"Error during secure navigation: {str(e)}")
            return None