"""Integration tests for Square login functionality."""
import pytest
import os
from pathlib import Path

# Test credentials
TEST_EMAIL = "joev+goosetestfree1@squareup.com"
TEST_PASSWORD = "password"

async def test_square_login_flow(browser):
    """Test complete Square login flow."""
    # Setup
    await browser.launch_browser()
    
    # Execute login
    success = await browser.square_login(TEST_EMAIL, TEST_PASSWORD)
    
    # Verify
    assert success == True
    assert 'dashboard' in browser._page.url.lower()

async def test_square_login_invalid_credentials(browser):
    """Test Square login with invalid credentials."""
    await browser.launch_browser()
    success = await browser.square_login("invalid@email.com", "wrongpassword")
    assert success == False

async def test_square_login_network_conditions(browser):
    """Test Square login under different network conditions."""
    await browser.launch_browser()
    
    # Test with slow connection
    await browser._page.route('**/*', lambda route: route.continue_(
        delay=1000  # Add 1s delay to all requests
    ))
    
    success = await browser.square_login(TEST_EMAIL, TEST_PASSWORD)
    assert success == True

@pytest.mark.skip(reason="For manual verification only")
async def test_square_login_debug_mode(browser):
    """Test Square login with debug mode and screenshots."""
    # Setup
    screenshots_dir = Path("test_screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    await browser.launch_browser()
    
    try:
        # Navigate to login page
        await browser._page.goto('https://app.squareupstaging.com/login')
        await browser._page.screenshot(path=str(screenshots_dir / "1_initial_page.png"))
        
        # Enter email
        email_input = browser._page.get_by_role('textbox', name='Email or phone number')
        await email_input.fill(TEST_EMAIL)
        await browser._page.screenshot(path=str(screenshots_dir / "2_email_entered.png"))
        
        # Click continue
        continue_button = browser._page.get_by_role('button', name='Continue')
        await continue_button.click()
        await browser._page.screenshot(path=str(screenshots_dir / "3_continue_clicked.png"))
        
        # Enter password
        password_input = browser._page.get_by_role('textbox', name='Password')
        await password_input.fill(TEST_PASSWORD)
        await browser._page.screenshot(path=str(screenshots_dir / "4_password_entered.png"))
        
        # Click sign in
        sign_in_button = browser._page.get_by_role('button', name='Sign in')
        await sign_in_button.click()
        await browser._page.screenshot(path=str(screenshots_dir / "5_sign_in_clicked.png"))
        
        # Wait for navigation
        await browser._page.wait_for_load_state('networkidle')
        await browser._page.screenshot(path=str(screenshots_dir / "6_final_state.png"))
        
        assert 'dashboard' in browser._page.url.lower()
    except Exception as e:
        await browser._page.screenshot(path=str(screenshots_dir / "error_state.png"))
        raise e