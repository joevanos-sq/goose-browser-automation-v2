"""Browser automation MCP server implementation."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from browser_automation.controllers.browser_controller import BrowserController
from browser_automation.controllers.square_controller import SquareController

# Initialize controllers
browser_controller = BrowserController()

# Initialize MCP server
mcp = FastMCP(
    name="browser-automation",
    description="Browser automation extension for Goose",
    tools=[
        {
            "name": "launch_browser",
            "description": "Launch a new browser instance",
            "parameters": {
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "description": "Whether to run in headless mode",
                        "default": False
                    }
                }
            }
        },
        {
            "name": "navigate_to",
            "description": "Navigate to a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "inspect_page",
            "description": "Inspect the current page content and structure",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector to target specific elements",
                        "default": "body"
                    }
                }
            }
        },
        {
            "name": "square_login",
            "description": "Login to Square using provided credentials",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Square account email"
                    },
                    "password": {
                        "type": "string",
                        "description": "Square account password"
                    }
                },
                "required": ["email", "password"]
            }
        }
    ]
)

# Tool Implementations
@mcp.tool()
async def launch_browser(params: Dict[str, Any]) -> Dict[str, Any]:
    """Launch a new browser instance."""
    try:
        headless = params.get("headless", False)
        await browser_controller.launch(headless=headless)
        return {
            "success": True,
            "message": "Browser launched successfully"
        }
    except Exception as e:
        error_data = ErrorData(code=INTERNAL_ERROR, message=str(e))
        raise McpError(error_data)

@mcp.tool()
async def navigate_to(params: Dict[str, Any]) -> Dict[str, Any]:
    """Navigate to a URL."""
    try:
        url = params.get("url")
        if not url:
            error_data = ErrorData(code=INVALID_PARAMS, message="URL is required")
            raise McpError(error_data)
            
        if not browser_controller.page:
            error_data = ErrorData(code=INVALID_PARAMS, message="Browser not launched. Call launch_browser first.")
            raise McpError(error_data)
            
        await browser_controller.navigate(url)
        return {
            "success": True,
            "message": f"Navigated to {url}"
        }
    except McpError:
        raise
    except Exception as e:
        error_data = ErrorData(code=INTERNAL_ERROR, message=f"Navigation failed: {str(e)}")
        raise McpError(error_data)

@mcp.tool()
async def inspect_page(params: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect the current page content and structure."""
    try:
        if not browser_controller.page:
            error_data = ErrorData(code=INVALID_PARAMS, message="Browser not launched. Call launch_browser first.")
            raise McpError(error_data)
            
        selector = params.get("selector", "body")
        
        # Get page content
        content = await browser_controller.inspect_page(selector)
        
        return {
            "success": True,
            "content": content
        }
    except McpError:
        raise
    except Exception as e:
        error_data = ErrorData(code=INTERNAL_ERROR, message=f"Page inspection failed: {str(e)}")
        raise McpError(error_data)

@mcp.tool()
async def square_login(params: Dict[str, Any]) -> Dict[str, Any]:
    """Login to Square using provided credentials."""
    try:
        email = params.get("email")
        password = params.get("password")
        
        if not email or not password:
            error_data = ErrorData(code=INVALID_PARAMS, message="Email and password are required")
            raise McpError(error_data)
            
        if not browser_controller.page:
            error_data = ErrorData(code=INVALID_PARAMS, message="Browser not launched. Call launch_browser first.")
            raise McpError(error_data)
            
        square = SquareController(browser_controller.page)
        success = await square.login(email, password)
        
        return {
            "success": success,
            "message": "Login successful" if success else "Login failed"
        }
    except McpError:
        raise
    except Exception as e:
        error_data = ErrorData(code=INTERNAL_ERROR, message=f"Login failed: {str(e)}")
        raise McpError(error_data)

def main():
    """Run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()