"""Browser automation MCP server implementation."""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

from browser_automation.controllers.browser_controller import BrowserController
from browser_automation.utils.selectors import GoogleSelectors

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
    submit: bool = False

@dataclass
class ClickElementParams:
    selector: str

@dataclass
class InspectPageParams:
    selector: str = "body"

@dataclass
class GoogleSearchParams:
    query: str
    click_index: Optional[int] = None
    click_text: Optional[str] = None
    ensure_visible: bool = True

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
    """Navigate to a URL.
    
    Note: For Google searches, use the google_search() function instead of navigating
    to google.com manually. This ensures more reliable search functionality."""
    try:
        nav_params = NavigateParams(**params)
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        # Add warning for manual Google navigation
        if "google.com" in nav_params.url.lower():
            logger.warning(
                "Warning: Attempting to navigate to Google directly. "
                "For better reliability, use the google_search() function instead."
            )
            
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
            
        success = await browser_controller.type_text(
            text_params.selector,
            text_params.text,
            submit=text_params.submit
        )
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
async def close_browser(params: Dict[str, Any]) -> Dict[str, Any]:
    """Close the current browser instance."""
    try:
        if not browser_controller.page:
            return {
                "success": True,
                "message": "No browser instance running"
            }
        await browser_controller.close()
        return {
            "success": True,
            "message": "Browser closed successfully"
        }
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Failed to close browser: {str(e)}")

@mcp.tool()
async def google_search(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a Google search with enhanced result handling.
    
    This is the recommended way to perform Google searches. It handles all the necessary steps:
    1. Navigating to google.com
    2. Locating the search input
    3. Entering the search query
    4. Submitting the search
    5. Waiting for results to load
    6. Optionally clicking a result
    
    Rather than using navigate_to() and type_text() manually, always use this method
    for Google searches as it uses reliable selectors and proper submission handling.
    
    Parameters:
        query (str): The search term to look up on Google
        click_index (int, optional): Index of result to click (1-based)
        click_text (str, optional): Text to match in result title
        ensure_visible (bool, optional): Whether to ensure result is in viewport before clicking
        
    Returns:
        Dict containing:
        - success (bool): Whether the search was successful
        - message (str): Status message about the operation
        - clicked (bool): Whether a result was successfully clicked
        - results (list, optional): List of result titles if available
    """
    try:
        # Validate and extract parameters
        search_params = GoogleSearchParams(**params)
        click_index = params.get('click_index')
        click_text = params.get('click_text')
        ensure_visible = params.get('ensure_visible', True)
        
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        # Navigate to Google
        nav_success = await browser_controller.navigate("https://www.google.com")
        if not nav_success:
            raise Exception("Failed to navigate to Google")
            
        # Perform search
        search_success = await browser_controller.type_text(
            GoogleSelectors.SEARCH['search_input'],
            search_params.query,
            submit=True
        )
        
        if not search_success:
            return {
                "success": False,
                "message": "Failed to perform search",
                "clicked": False
            }
            
        # Wait for results to load
        results_ready = await browser_controller.wait_for_search_results()
        if not results_ready:
            return {
                "success": True,
                "message": "Search completed but results not found",
                "clicked": False
            }
            
        # Get result titles for reference
        result_titles = await browser_controller.get_result_texts()
        
        # Click result if requested
        clicked = False
        if click_index:
            clicked = await browser_controller.click_result_by_index(click_index, ensure_visible)
        elif click_text:
            clicked = await browser_controller.click_result_by_text(click_text, ensure_visible)
        
        return {
            "success": True,
            "message": "Search completed successfully",
            "clicked": clicked,
            "results": result_titles
        }
    except ValueError as e:
        raise make_error(INVALID_PARAMS, str(e))
    except Exception as e:
        raise make_error(INTERNAL_ERROR, f"Search failed: {str(e)}")

def main() -> None:
    """Run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()