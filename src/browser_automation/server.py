"""Browser automation MCP server implementation."""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

from browser_automation.controllers.browser_controller import BrowserController
from browser_automation.controllers.square_controller import SquareController

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Parameter Models
@dataclass
class BrowserLaunchParams:
    headless: bool = False

@dataclass
class NavigateParams:
    url: str

@dataclass
class TypeTextParams:
    selector: str
    text: str

@dataclass
class ClickElementParams:
    selector: str

@dataclass
class InspectPageParams:
    selector: str = "body"

@dataclass
class SquareLoginParams:
    email: str
    password: str

# Initialize controllers
browser_controller = BrowserController()

# Initialize MCP server
mcp = FastMCP(
    name="browser-automation",
    description="Browser automation extension for Goose"
)

def make_error(code: int, message: str) -> McpError:
    """Create an MCP error with proper error data."""
    return McpError(ErrorData(code=code, message=message))

@mcp.tool()
async def launch_browser(params: Dict[str, Any]) -> Dict[str, Any]:
    """Launch a new browser instance."""
    try:
        launch_params = BrowserLaunchParams(**params)
        success = await browser_controller.launch(headless=launch_params.headless)
        return {
            "success": success,
            "message": "Browser launched successfully" if success else "Failed to launch browser"
        }
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Failed to launch browser: {str(e)}")

@mcp.tool()
async def navigate_to(params: Dict[str, Any]) -> Dict[str, Any]:
    """Navigate to a URL."""
    try:
        nav_params = NavigateParams(**params)
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        success = await browser_controller.navigate(nav_params.url)
        return {
            "success": success,
            "message": f"Navigated to {nav_params.url}" if success else f"Failed to navigate to {nav_params.url}"
        }
    except ValueError as e:
        raise make_error(INVALID_PARAMS, str(e))
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Navigation failed: {str(e)}")

@mcp.tool()
async def type_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """Type text into an element."""
    try:
        text_params = TypeTextParams(**params)
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        success = await browser_controller.type_text(text_params.selector, text_params.text)
        return {
            "success": success,
            "message": f"Typed text into {text_params.selector}" if success else f"Failed to type text into {text_params.selector}"
        }
    except ValueError as e:
        raise make_error(INVALID_PARAMS, str(e))
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Failed to type text: {str(e)}")

@mcp.tool()
async def click_element(params: Dict[str, Any]) -> Dict[str, Any]:
    """Click on an element."""
    try:
        click_params = ClickElementParams(**params)
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        success = await browser_controller.click_element(click_params.selector)
        return {
            "success": success,
            "message": f"Clicked {click_params.selector}" if success else f"Failed to click {click_params.selector}"
        }
    except ValueError as e:
        raise make_error(INVALID_PARAMS, str(e))
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Failed to click element: {str(e)}")

@mcp.tool()
async def inspect_page(params: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect the current page content and structure."""
    try:
        inspect_params = InspectPageParams(**params)
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        content = await browser_controller.inspect_page(inspect_params.selector)
        return {
            "success": True,
            "content": content
        }
    except ValueError as e:
        raise make_error(INVALID_PARAMS, str(e))
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Page inspection failed: {str(e)}")

@mcp.tool()
async def square_login(params: Dict[str, Any]) -> Dict[str, Any]:
    """Login to Square using provided credentials."""
    try:
        login_params = SquareLoginParams(**params)
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        square = SquareController(browser_controller.page)
        success = await square.login(
            email=login_params.email,
            password=login_params.password
        )
        
        return {
            "success": success,
            "message": "Login successful" if success else "Login failed"
        }
    except ValueError as e:
        raise make_error(INVALID_PARAMS, str(e))
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Login failed: {str(e)}")

@mcp.tool()
async def close_browser(params: Dict[str, Any]) -> Dict[str, Any]:
    """Close the browser and clean up resources."""
    try:
        await browser_controller.close()
        return {
            "success": True,
            "message": "Browser closed successfully"
        }
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Failed to close browser: {str(e)}")

def main() -> None:
    """Run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()