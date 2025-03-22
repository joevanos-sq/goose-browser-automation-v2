"""End-to-end tests for MCP server integration."""
import pytest
from browser_automation.server import mcp

async def test_mcp_launch_browser_tool(mcp_server):
    """Test MCP launch_browser tool."""
    result = await mcp_server.tools["launch_browser"]({})
    assert result["success"] == True
    assert "Browser launched successfully" in result["message"]

async def test_mcp_square_login_tool(mcp_server):
    """Test MCP square_login tool."""
    # First launch browser
    await mcp_server.tools["launch_browser"]({})
    
    # Then attempt login
    result = await mcp_server.tools["square_login"]({
        "email": "joev+goosetestfree1@squareup.com",
        "password": "password"
    })
    
    assert result["success"] == True
    assert "Login successful" in result["message"]

async def test_mcp_parameter_validation(mcp_server):
    """Test MCP parameter validation."""
    # Test missing email
    result = await mcp_server.tools["square_login"]({
        "password": "password"
    })
    assert result["success"] == False
    assert "required" in result["message"].lower()
    
    # Test missing password
    result = await mcp_server.tools["square_login"]({
        "email": "test@example.com"
    })
    assert result["success"] == False
    assert "required" in result["message"].lower()

async def test_mcp_error_handling(mcp_server):
    """Test MCP error handling."""
    # Test login without launching browser
    result = await mcp_server.tools["square_login"]({
        "email": "test@example.com",
        "password": "password"
    })
    assert result["success"] == False
    assert "browser not launched" in result["message"].lower()