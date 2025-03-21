"""Integration tests for Square login automation."""
import pytest
from playwright.async_api import Page
from ...src.browser_automation.controllers.square_controller_new import SquareController


@pytest.mark.integration
@pytest.mark.asyncio
async def test_square_login_components(page: Page):
    """Test Square login page component detection."""
    controller = SquareController(page)
    
    # Navigate to login page
    await page.goto('https://app.squareupstaging.com/login')
    
    # Test web component detection
    await controller.wait_for_square_components()
    
    # Test email field detection
    await controller.locator.find_element({'id': 'mpui-combo-field-input'})
    
    # Test continue button detection (should find with one of the selectors)
    found_button = False
    selectors = [
        {'test_id': 'login-email-next-button'},
        {'role': 'button', 'text': 'Continue'},
        {'tag': 'market-button', 'test_id': 'login-email-next-button'}
    ]
    
    for selector in selectors:
        if await controller.locator.is_element_present(selector):
            found_button = True
            break
            
    assert found_button, "Continue button not found with any selector"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_square_login_flow(page: Page):
    """Test complete Square login flow."""
    controller = SquareController(page)
    
    # Use test credentials
    email = "test@example.com"
    password = "password123"
    
    # Start login flow
    result = await controller.login(email, password)
    
    # We expect this to fail with test credentials
    assert not result, "Login should fail with test credentials"
    
    # But we should have gotten to the password screen
    assert await controller.locator.is_element_present({'type': 'password'}), \
        "Password field not found"