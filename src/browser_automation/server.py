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

[... rest of the file remains the same ...]