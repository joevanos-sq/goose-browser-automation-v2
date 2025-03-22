"""Browser automation MCP server implementation."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import Dict, Any, Optional

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
        },
        {
            "name": "close_browser",
            "description": "Close the browser and clean up resources",
            "parameters": {
                "type": "object",
                "properties": {}
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
        success = await browser_controller.launch(headless=headless)
        return {
            "success": success,
            "message": "Browser launched successfully" if success else "Failed to launch browser"
        }
    except Exception as e:
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Failed to launch browser: {str(e)}")
        )

@mcp.tool()
async def navigate_to(params: Dict[str, Any]) -> Dict[str, Any]:
    """Navigate to a URL."""
    try:
        url = params.get("url")
        if not url:
            raise ValueError("URL is required")
            
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        success = await browser_controller.navigate(url)
        return {
            "success": success,
            "message": f"Navigated to {url}" if success else f"Failed to navigate to {url}"
        }
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e)))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Navigation failed: {str(e)}"))

@mcp.tool()
async def inspect_page(params: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect the current page content and structure."""
    try:
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        selector = params.get("selector", "body")
        
        # Get page content
        content = await browser_controller.inspect_page(selector)
        
        return {
            "success": True,
            "content": content
        }
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e)))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Page inspection failed: {str(e)}"))

@mcp.tool()
async def square_login(params: Dict[str, Any]) -> Dict[str, Any]:
    """Login to Square using provided credentials."""
    try:
        email = params.get("email")
        password = params.get("password")
        
        if not email or not password:
            raise ValueError("Email and password are required")
            
        if not browser_controller.page:
            raise ValueError("Browser not launched. Call launch_browser first.")
            
        square = SquareController(browser_controller.page)
        success = await square.login(email, password)
        
        return {
            "success": success,
            "message": "Login successful" if success else "Login failed"
        }
    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e)))
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Login failed: {str(e)}"))

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
        raise McpError(ErrorData(INTERNAL_ERROR, f"Failed to close browser: {str(e)}"))

def main():
    """Run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()