"""Unit tests for browser automation core functionality."""
import pytest
from playwright.async_api import Error as PlaywrightError

from browser_automation.controllers.browser_controller import BrowserController

async def test_browser_launch(browser: BrowserController) -> None:
    """Test browser launch and initialization."""
    assert browser.page is not None
    assert browser._browser is not None

async def test_browser_navigation(browser: BrowserController) -> None:
    """Test browser navigation."""
    assert browser.page is not None
    success = await browser.navigate('https://www.google.com')
    assert success is True
    assert 'google.com' in browser.page.url

async def test_type_text(browser: BrowserController) -> None:
    """Test typing text into elements."""
    assert browser.page is not None
    await browser.navigate('https://www.google.com')
    
    success = await browser.type_text('Search', 'test search')
    assert success is True

async def test_click_element(browser: BrowserController) -> None:
    """Test clicking elements."""
    assert browser.page is not None
    await browser.navigate('https://www.google.com')
    
    success = await browser.click_element('About')
    assert success is True

async def test_browser_cleanup(browser: BrowserController) -> None:
    """Test browser cleanup."""
    await browser.close()
    assert browser._browser is None
    assert browser._page is None
    assert browser._playwright is None