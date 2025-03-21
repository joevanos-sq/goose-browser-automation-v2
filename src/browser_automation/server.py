"""Browser automation MCP server implementation."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import Dict, Any, Optional

# Import directly from module files
from .controllers.browser_controller import BrowserController
from .controllers.square_controller import SquareController

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