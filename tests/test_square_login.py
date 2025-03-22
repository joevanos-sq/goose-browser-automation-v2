"""Test script for Square login with debugging."""
import asyncio
from browser_automation.controllers.browser_controller import BrowserController
from browser_automation.utils.logging_utils import DebugLogger

logger = DebugLogger().logger

async def test_square_login():
    """Test Square login functionality with debugging."""
    browser = BrowserController()
    
    try:
        # Launch browser in non-headless mode
        logger.info("Launching browser...")
        await browser.launch(headless=False)
        
        # Navigate to Square login
        logger.info("Navigating to Square login...")
        await browser.navigate("https://app.squareupstaging.com/login")
        
        # Wait for initial page load
        await browser.page.wait_for_load_state('networkidle')
        logger.info("Page loaded")
        
        # Wait for and verify email input presence
        email_input = await browser.page.wait_for_selector(
            'input[data-testid="username-input"]',
            state='visible',
            timeout=10000
        )
        
        if not email_input:
            logger.error("Email input not found")
            return
            
        logger.info("Found email input")
        
        # Fill email
        await email_input.fill('joev+goosetestfree1@squareup.com')
        logger.info("Filled email")
        
        # Find and click next button
        next_button = await browser.page.wait_for_selector(
            'market-button[data-testid="login-email-next-button"]',
            state='visible',
            timeout=5000
        )
        
        if not next_button:
            logger.error("Next button not found")
            
            # Debug: List all buttons
            buttons = await browser.page.evaluate("""() => {
                return Array.from(document.querySelectorAll('market-button')).map(btn => ({
                    tag: btn.tagName,
                    text: btn.textContent?.trim(),
                    'data-testid': btn.getAttribute('data-testid'),
                    class: btn.className
                }));
            }""")
            logger.info("Available market-buttons:")
            for button in buttons:
                logger.info(f"  {button}")
                
            return
            
        logger.info("Found next button")
        await next_button.click()
        logger.info("Clicked next button")
        
        # Wait for password input
        password_input = await browser.page.wait_for_selector(
            'input[type="password"]',
            state='visible',
            timeout=10000
        )
        
        if not password_input:
            logger.error("Password input not found")
            return
            
        logger.info("Found password input")
        
        # Fill password
        await password_input.fill('password')
        logger.info("Filled password")
        
        # Find and click sign in button
        sign_in_button = await browser.page.wait_for_selector(
            'market-button[data-testid="login-password-next-button"]',
            state='visible',
            timeout=5000
        )
        
        if not sign_in_button:
            logger.error("Sign in button not found")
            return
            
        logger.info("Found sign in button")
        await sign_in_button.click()
        logger.info("Clicked sign in button")
        
        # Wait for navigation
        await browser.page.wait_for_load_state('networkidle')
        
        # Check final URL
        current_url = browser.page.url
        logger.info(f"Final URL: {current_url}")
        
        if 'dashboard' in current_url or 'home' in current_url:
            logger.info("Login successful!")
        else:
            logger.error("Login may have failed")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        # Take a screenshot if something fails
        if browser.page:
            await browser.page.screenshot(path='error.png')
    finally:
        # Wait a bit to see the result
        await asyncio.sleep(3)
        # Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_square_login())