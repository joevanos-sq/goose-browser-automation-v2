"""Integration tests for Square login functionality."""
import pytest
from browser_automation.controllers.browser_controller import BrowserController
from browser_automation.controllers.square_controller import SquareController

# Test credentials
TEST_EMAIL = "joev+goosetestfree1@squareup.com"
TEST_PASSWORD = "password"

async def test_square_login_flow(browser: BrowserController) -> None:
    """Test complete Square login flow."""
    assert browser.page is not None
    
    # Create Square controller
    square = SquareController(browser.page)
    
    # Execute login
    success = await square.login(TEST_EMAIL, TEST_PASSWORD)
    
    # Verify
    assert success is True
    assert browser.page.url is not None
    assert 'dashboard' in browser.page.url.lower()

async def test_square_login_invalid_credentials(browser: BrowserController) -> None:
    """Test Square login with invalid credentials."""
    assert browser.page is not None
    
    # Create Square controller
    square = SquareController(browser.page)
    
    # Try invalid login
    success = await square.login("invalid@email.com", "wrongpassword")
    assert success is False