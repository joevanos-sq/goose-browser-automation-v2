"""Test the enhanced inspector functionality."""
import pytest
import asyncio
from browser_automation.controllers.browser_controller import BrowserController

@pytest.mark.asyncio
async def test_enhanced_inspector():
    """Test the enhanced inspector with various options."""
    controller = BrowserController()
    
    # Launch browser
    result = await controller.launch_browser(headless=True)
    assert result["success"], "Failed to launch browser"
    
    try:
        # Navigate to a test page
        result = await controller.navigate_to("https://example.com")
        assert result["success"], "Failed to navigate to page"
        
        # Test default inspection
        result = await controller.inspect_page()
        assert result["success"], "Failed to inspect page with default options"
        assert "data" in result, "No data returned from inspection"
        assert "url" in result["data"], "URL not found in inspection data"
        
        # Test inspection with custom options
        custom_options = {
            "max_inputs": 5,
            "max_components": 5,
            "text_length": 30,
            "include_inputs": True,
            "include_components": False
        }
        result = await controller.inspect_page(custom_options)
        assert result["success"], "Failed to inspect page with custom options"
        assert "data" in result, "No data returned from custom inspection"
        assert "webComponents" not in result["data"], "Web components included when disabled"
        
        # Test element inspection
        result = await controller.inspect_element("h1")
        assert result["success"], "Failed to inspect h1 element"
        assert "data" in result, "No data returned from element inspection"
        assert result["data"]["tag"] == "h1", "Wrong element tag returned"
        
    finally:
        # Clean up
        await controller.close_browser()

if __name__ == "__main__":
    asyncio.run(test_enhanced_inspector())