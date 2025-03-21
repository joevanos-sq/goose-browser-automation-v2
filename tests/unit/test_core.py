"""Tests for core browser automation components."""
import pytest
from playwright.async_api import Page
from ...src.browser_automation.core.exceptions import (
    ElementNotFoundError,
    WebComponentError
)
from ...src.browser_automation.core.web_component_handler import WebComponentHandler
from ...src.browser_automation.core.element_locator import ElementLocator


@pytest.mark.asyncio
async def test_web_component_handler(page: Page):
    """Test web component handling."""
    handler = WebComponentHandler(page)
    
    # Create a test page with web components
    await page.set_content("""
        <script>
            class TestButton extends HTMLElement {
                constructor() {
                    super();
                    this.attachShadow({mode: 'open'});
                    this.shadowRoot.innerHTML = '<button>Click me</button>';
                }
            }
            customElements.define('test-button', TestButton);
        </script>
        <test-button id="test-btn"></test-button>
    """)
    
    # Test waiting for components
    await handler.wait_for_components(['test-button'])
    
    # Test waiting for shadow root
    await handler.wait_for_shadow_root('test-button')
    
    # Test getting component info
    info = await handler.get_component_info('test-button')
    assert info['tagName'] == 'test-button'
    assert info['hasShadowRoot'] is True
    
    # Test finding components
    components = await handler.find_components_by_type('test-button')
    assert len(components) == 1
    assert components[0]['id'] == 'test-btn'
    
    # Test error handling
    with pytest.raises(WebComponentError):
        await handler.wait_for_components(['non-existent'], timeout=1000)


@pytest.mark.asyncio
async def test_element_locator(page: Page):
    """Test element location strategies."""
    locator = ElementLocator(page)
    
    # Create a test page with various elements
    await page.set_content("""
        <div data-testid="test-div">Test Div</div>
        <button role="button">Click Me</button>
        <label for="test-input">Test Label</label>
        <input id="test-input" placeholder="Enter text">
        <span class="test-class">Test Span</span>
    """)
    
    # Test finding by test ID
    element = await locator.find_element({'test_id': 'test-div'})
    assert await element.inner_text() == 'Test Div'
    
    # Test finding by role
    element = await locator.find_element({'role': 'button'})
    assert await element.inner_text() == 'Click Me'
    
    # Test finding by label
    element = await locator.find_element({'label': 'Test Label'})
    assert await element.get_attribute('for') == 'test-input'
    
    # Test finding by placeholder
    element = await locator.find_element({'placeholder': 'Enter text'})
    assert await element.get_attribute('id') == 'test-input'
    
    # Test finding by class
    element = await locator.find_element({'class_name': 'test-class'})
    assert await element.inner_text() == 'Test Span'
    
    # Test error handling
    with pytest.raises(ElementNotFoundError):
        await locator.find_element({'test_id': 'non-existent'}, timeout=1000)
    
    # Test element presence check
    assert await locator.is_element_present({'test_id': 'test-div'})
    assert not await locator.is_element_present({'test_id': 'non-existent'})