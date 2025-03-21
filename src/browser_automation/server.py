"""Browser automation MCP server implementation."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import Dict, Any, Optional

# Import from controllers package
from browser_automation.controllers import BrowserController, SquareController

# Initialize controllers
browser_controller = BrowserController()

[... rest of the file remains the same ...]