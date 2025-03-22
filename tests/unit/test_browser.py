"""Unit tests for browser automation core functionality."""
import pytest
from playwright.async_api import Error as PlaywrightError
from browser_automation.server import BrowserAutomation

async def test_browser_launch(browser):
    """Test browser launch functionality."""
    success = await browser.launch_browser()
    assert success == True
    assert browser._browser is not None
    assert browser._page is not None

async def test_browser_navigation(browser):
    """Test browser navigation."""
    await browser.launch_browser()
    await browser._page.goto('about:blank')
    assert browser._page.url == 'about:blank'

async def test_browser_cleanup(browser):
    """Test browser cleanup."""
    await browser.launch_browser()
    await browser.close()
    assert browser._browser is None or browser._browser.is_closed()

@pytest.mark.parametrize("invalid_url", [
    "not-a-url",
    "invalid://protocol",
    "",
])
async def test_invalid_navigation(browser, invalid_url):
    """Test handling of invalid navigation attempts."""
    await browser.launch_browser()
    with pytest.raises(PlaywrightError):
        await browser._page.goto(invalid_url)

async def test_multiple_browser_instances():
    """Test handling of multiple browser instances."""
    browser1 = BrowserAutomation(debug=True)
    browser2 = BrowserAutomation(debug=True)
    
    try:
        success1 = await browser1.launch_browser()
        success2 = await browser2.launch_browser()
        
        assert success1 == True
        assert success2 == True
        assert browser1._browser is not None
        assert browser2._browser is not None
    finally:
        await browser1.close()
        await browser2.close()