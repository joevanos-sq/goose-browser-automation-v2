"""Browser automation extension for Goose."""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import logging
from .controllers.browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize browser automation
browser_controller = BrowserController()

# Initialize MCP server
mcp = FastMCP(
    name="browser-automation",
    description="Browser automation extension for Goose",
    tools=[
        {
            "name": "launch_browser",
            "description": "Launch a new Chromium browser instance",
            "parameters": {
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "description": "Whether to run in headless mode",
                        "default": False
                    },
                    "viewport": {
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "default": 1280},
                            "height": {"type": "integer", "default": 720}
                        }
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
            "description": "Close the current browser instance and clean up resources",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]
)

@mcp.tool("launch_browser")
async def launch_browser(params: Dict[str, Any]) -> Dict[str, Any]:
    """Launch a new Chromium browser instance."""
    try:
        headless = params.get("headless", False)
        viewport = params.get("viewport")
        
        success = await browser_controller.launch(
            headless=headless,
            viewport=viewport
        )
        
        if not success:
            raise McpError(ErrorData(
                INTERNAL_ERROR,
                "Failed to launch browser"
            ))
            
        return {
            "success": True,
            "message": "Browser launched successfully"
        }
    except Exception as e:
        logger.error(f"Failed to launch browser: {str(e)}")
        raise McpError(ErrorData(
            INTERNAL_ERROR,
            f"Failed to launch browser: {str(e)}"
        ))

@mcp.tool("square_login")
async def square_login(params: Dict[str, Any]) -> Dict[str, Any]:
    """Login to Square using provided credentials."""
    try:
        email = params.get("email")
        password = params.get("password")
        
        if not email or not password:
            raise McpError(ErrorData(
                INVALID_PARAMS,
                "Email and password are required"
            ))
            
        if not browser_controller.page:
            raise McpError(ErrorData(
                INVALID_PARAMS,
                "Browser not launched. Call launch_browser first."
            ))
            
        # Get Square controller
        square = browser_controller.get_square_controller()
        if not square:
            raise McpError(ErrorData(
                INTERNAL_ERROR,
                "Failed to get Square controller"
            ))
            
        # Perform login
        success = await square.login(email=email, password=password)
        
        if not success:
            raise McpError(ErrorData(
                INTERNAL_ERROR,
                "Login failed"
            ))
            
        return {
            "success": True,
            "message": "Login successful"
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise McpError(ErrorData(
            INTERNAL_ERROR,
            f"Login failed: {str(e)}"
        ))

@mcp.tool("close_browser")
async def close_browser(params: Dict[str, Any]) -> Dict[str, Any]:
    """Close browser and clean up resources."""
    try:
        await browser_controller.close()
        return {
            "success": True,
            "message": "Browser closed successfully"
        }
    except Exception as e:
        logger.error(f"Failed to close browser: {str(e)}")
        raise McpError(ErrorData(
            INTERNAL_ERROR,
            f"Failed to close browser: {str(e)}"
        ))

def main():
    """Run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()