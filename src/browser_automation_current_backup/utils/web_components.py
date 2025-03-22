"""Utilities for handling web components and shadow DOM."""
import logging
from typing import Optional, List, Dict, Any
from playwright.async_api import Page, ElementHandle, TimeoutError

logger = logging.getLogger(__name__)

class WebComponentUtils:
    """Utilities for working with web components and shadow DOM."""
    
    def __init__(self, page: Page):
        self.page = page
        
    async def wait_for_web_component(self, selector: str, timeout: int = 30000) -> Optional[ElementHandle]:
        """
        Wait for a web component to be defined and ready.
        
        Args:
            selector: Component selector (tag name)
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            ElementHandle if found, None otherwise
        """
        try:
            # Wait for element to be present
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            if not element:
                return None
                
            # Wait for custom element to be defined
            is_defined = await self.page.evaluate(f"""(selector) => {{
                return customElements.get(selector.toLowerCase()) !== undefined;
            }}, "{selector}")""")
            
            if not is_defined:
                logger.warning(f"Custom element {selector} not defined")
                return None
                
            return element
            
        except TimeoutError:
            logger.error(f"Timeout waiting for web component: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for web component: {str(e)}")
            return None
            
    async def get_shadow_element(self, host: ElementHandle, selector: str) -> Optional[ElementHandle]:
        """
        Find an element within a shadow DOM.
        
        Args:
            host: Shadow host element
            selector: Selector within shadow DOM
            
        Returns:
            ElementHandle if found, None otherwise
        """
        try:
            # Check if element has shadow root
            has_shadow = await self.page.evaluate("""(element) => {
                return element.shadowRoot !== null;
            }""", host)
            
            if not has_shadow:
                logger.warning(f"No shadow root found for element")
                return None
                
            # Find element in shadow DOM
            shadow_element = await host.evaluate(f"""(element, selector) => {{
                return element.shadowRoot.querySelector(selector);
            }}, "{selector}")""")
            
            if not shadow_element:
                return None
                
            return shadow_element
            
        except Exception as e:
            logger.error(f"Error accessing shadow DOM: {str(e)}")
            return None
            
    async def fill_shadow_input(self, component_selector: str, input_selector: str, value: str) -> bool:
        """
        Fill an input field within a shadow DOM.
        
        Args:
            component_selector: Web component selector
            input_selector: Input selector within shadow DOM
            value: Value to fill
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Wait for web component
            component = await self.wait_for_web_component(component_selector)
            if not component:
                return False
                
            # Fill input using JavaScript for reliability
            success = await self.page.evaluate(f"""(component, inputSelector, value) => {{
                const input = component.shadowRoot.querySelector(inputSelector);
                if (!input) return false;
                
                // Set value and dispatch events
                input.value = value;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}, "{input_selector}", "{value}")""")
            
            return success
            
        except Exception as e:
            logger.error(f"Error filling shadow input: {str(e)}")
            return False
            
    async def click_shadow_button(self, component_selector: str, button_selector: str) -> bool:
        """
        Click a button within a shadow DOM.
        
        Args:
            component_selector: Web component selector
            button_selector: Button selector within shadow DOM
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Wait for web component
            component = await self.wait_for_web_component(component_selector)
            if not component:
                return False
                
            # Click button using JavaScript for reliability
            success = await self.page.evaluate(f"""(component, buttonSelector) => {{
                const button = component.shadowRoot.querySelector(buttonSelector);
                if (!button) return false;
                
                // Simulate click
                button.click();
                return true;
            }}, "{button_selector}")""")
            
            return success
            
        except Exception as e:
            logger.error(f"Error clicking shadow button: {str(e)}")
            return False
            
    async def wait_for_component_state(self, component_selector: str, state_check: str) -> bool:
        """
        Wait for a web component to reach a certain state.
        
        Args:
            component_selector: Web component selector
            state_check: JavaScript expression to check component state
            
        Returns:
            bool: True if state is reached, False otherwise
        """
        try:
            # Wait for state using polling
            success = await self.page.wait_for_function(f"""(selector, check) => {{
                const component = document.querySelector(selector);
                if (!component) return false;
                return {state_check};
            }}, "{component_selector}")""")
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"Error waiting for component state: {str(e)}")
            return False
            
    async def get_component_property(self, component_selector: str, property_name: str) -> Any:
        """
        Get a property value from a web component.
        
        Args:
            component_selector: Web component selector
            property_name: Name of the property to get
            
        Returns:
            Property value or None if not found
        """
        try:
            value = await self.page.evaluate(f"""(selector, prop) => {{
                const component = document.querySelector(selector);
                if (!component) return null;
                return component[prop];
            }}, "{component_selector}", "{property_name}")""")
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting component property: {str(e)}")
            return None