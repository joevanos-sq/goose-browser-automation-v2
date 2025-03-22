"""Browser automation extension for Goose using Playwright."""
import json
import sys
import asyncio
import signal
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, cast
from playwright.async_api import async_playwright, Browser, Page, Playwright, Error as PlaywrightError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path.home() / '.goose' / 'logs' / 'browser_automation.log')
    ]
)
logger = logging.getLogger('browser_automation')

class BrowserAutomationExtension:
    """Browser automation extension using Playwright."""
    
    def __init__(self) -> None:
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._shutting_down: bool = False
        self.tools = [
            {
                "name": "launch_browser",
                "description": "Launch Chrome Canary browser",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "navigate_to",
                "description": "Navigate to a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "square_login",
                "description": "Login to Square staging",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "password": {"type": "string"}
                    },
                    "required": ["email", "password"]
                }
            }
        ]

    async def ensure_browser(self) -> bool:
        """Ensure browser is running."""
        try:
            if not self._playwright:
                logger.info("Initializing Playwright...")
                self._playwright = await async_playwright().start()
                
            if not self._browser:
                if not self._playwright:
                    raise ValueError("Playwright not initialized")
                logger.info("Launching Chrome Canary...")
                self._browser = await self._playwright.chromium.launch(
                    channel="chrome-canary",
                    headless=False
                )
                
            if not self._page:
                if not self._browser:
                    raise ValueError("Browser not initialized")
                logger.info("Creating new page...")
                self._page = await self._browser.new_page()
                
            return True
        except PlaywrightError as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error initializing browser: {e}")
            return False

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self._shutting_down = True
            if self._page:
                await self._page.close()
                self._page = None
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def square_login(self, email: str, password: str) -> bool:
        """Handle Square login flow."""
        try:
            if not self._page:
                raise ValueError("Browser page not initialized")
                
            logger.info("Starting Square login...")
            
            # Navigate to login page
            await self._page.goto('https://app.squareupstaging.com/login')
            logger.info("Navigated to login page")

            # Fill email
            email_input = self._page.get_by_role('textbox', name='Email or phone number')
            await email_input.fill(email)
            logger.info("Filled email")

            # Click continue
            continue_button = self._page.get_by_role('button', name='Continue')
            await continue_button.click()
            logger.info("Clicked continue")

            # Fill password
            password_input = self._page.get_by_role('textbox', name='Password')
            await password_input.fill(password)
            logger.info("Filled password")

            # Click sign in
            sign_in_button = self._page.get_by_role('button', name='Sign in')
            await sign_in_button.click()
            logger.info("Clicked sign in")

            # Wait for navigation
            await self._page.wait_for_load_state('networkidle')
            logger.info("Login complete")
            
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

# Initialize extension
extension = BrowserAutomationExtension()

async def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle incoming JSON-RPC requests."""
    try:
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        # Handle notifications
        if method.startswith("notifications/"):
            logger.debug(f"Handling notification: {method}")
            if method == "notifications/shutdown":
                logger.info("Received shutdown notification")
                extension._shutting_down = True
            return None

        # Handle initialization
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "name": "browser-automation",
                    "description": "Browser automation extension for Goose",
                    "protocolVersion": "1.0.0",
                    "serverInfo": {
                        "name": "browser-automation",
                        "version": "1.0.0",
                        "vendor": "Block",
                        "platform": "python",
                        "supportedProtocolVersions": ["1.0.0"]
                    },
                    "capabilities": {
                        "tools": {
                            "enabled": True
                        },
                        "resources": {
                            "enabled": False
                        },
                        "prompts": {
                            "enabled": False,
                            "models": []
                        }
                    },
                    "tools": extension.tools
                }
            }

        # Handle tools/list
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": extension.tools
            }

        # Handle tool calls
        if method == "launch_browser":
            success = await extension.ensure_browser()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": "Browser launched successfully" if success else "Failed to launch browser"
            }

        if method == "navigate_to":
            if not extension._page:
                raise ValueError("Browser not launched")
            url = cast(str, params.get("url"))
            await extension._page.goto(url)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": f"Navigated to {url}"
            }

        if method == "square_login":
            if not extension._page:
                raise ValueError("Browser not launched")
            email = cast(str, params.get("email"))
            password = cast(str, params.get("password"))
            success = await extension.square_login(email, password)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": "Login successful" if success else "Login failed"
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method {method} not found"}
        }

    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": str(e)}
        }

def handle_sigterm(signum: int, frame: Any) -> None:
    """Handle SIGTERM signal."""
    logger.info("Received SIGTERM")
    if extension._event_loop:
        extension._event_loop.create_task(extension.cleanup())
    sys.exit(0)

async def main() -> None:
    """Main extension loop."""
    logger.info("Starting browser automation extension")
    
    # Store event loop for cleanup
    extension._event_loop = asyncio.get_event_loop()
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    while not extension._shutting_down:
        try:
            # Read request from stdin
            line = sys.stdin.readline()
            if not line:
                logger.info("Received EOF, shutting down")
                break

            # Parse request
            request = json.loads(line)
            logger.debug(f"Received request: {request}")

            # Handle request
            response = await handle_request(request)
            
            # Send response (if any)
            if response is not None:
                print(json.dumps(response), flush=True)
                logger.debug(f"Sent response: {response}")

        except json.JSONDecodeError:
            # Ignore empty lines
            continue
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

    # Cleanup on exit
    await extension.cleanup()
    logger.info("Extension stopped")

if __name__ == "__main__":
    # Run in asyncio event loop
    asyncio.run(main())