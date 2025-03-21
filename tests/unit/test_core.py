"""Tests for core browser automation components."""
import pytest
from playwright.sync_api import Page, sync_playwright
from browser_automation.core.exceptions import (
    ElementNotFoundError,
    WebComponentError
)


def test_web_component_handler(page: Page):
    """Test web component handling."""
    # Create a test page with web components
    page.set_content("""
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
    
    # Test web component detection
    assert page.evaluate("""() => {
        return customElements.get('test-button') !== undefined;
    }""")
    
    # Test shadow root
    assert page.evaluate("""() => {
        const el = document.querySelector('test-button');
        return el && el.shadowRoot !== null;
    }""")
    
    # Test component info
    info = page.evaluate("""() => {
        const el = document.querySelector('test-button');
        return {
            tagName: el.tagName.toLowerCase(),
            hasShadowRoot: !!el.shadowRoot,
            id: el.id
        };
    }""")
    
    assert info['tagName'] == 'test-button'
    assert info['hasShadowRoot'] is True
    assert info['id'] == 'test-btn'


def test_element_location(page: Page):
    """Test element location strategies."""
    # Create a test page with various elements
    page.set_content("""
        <div data-testid="test-div">Test Div</div>
        <button role="button">Click Me</button>
        <label for="test-input">Test Label</label>
        <input id="test-input" placeholder="Enter text">
        <span class="test-class">Test Span</span>
    """)
    
    # Test finding by test ID
    element = page.locator('[data-testid="test-div"]')
    assert element.inner_text() == 'Test Div'
    
    # Test finding by role
    element = page.locator('[role="button"]')
    assert element.inner_text() == 'Click Me'
    
    # Test finding by label
    element = page.locator('label[for="test-input"]')
    assert element.get_attribute('for') == 'test-input'
    
    # Test finding by placeholder
    element = page.locator('[placeholder="Enter text"]')
    assert element.get_attribute('id') == 'test-input'
    
    # Test finding by class
    element = page.locator('.test-class')
    assert element.inner_text() == 'Test Span'
    
    # Test element presence
    assert page.locator('[data-testid="test-div"]').is_visible()
    assert not page.locator('[data-testid="non-existent"]').is_visible()