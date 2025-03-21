"""Web component handling utilities."""
import logging
from typing import List, Optional, Dict, Any
from playwright.async_api import Page
from .exceptions import WebComponentError

logger = logging.getLogger(__name__)


class WebComponentHandler:
    """Handles web component interactions and state."""
    
    def __init__(self, page: Page):
        """Initialize the handler with a page instance."""
        self.page = page
        
    async def wait_for_components(
        self,
        components: List[str],
        timeout: int = 30000
    ) -> None:
        """
        Wait for web components to be defined.
        
        Args:
            components: List of component names to wait for
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            WebComponentError: If components are not defined within timeout
        """
        try:
            checks = " && ".join([
                f"customElements.get('{name}') !== undefined"
                for name in components
            ])
            
            await self.page.wait_for_function(
                f"""() => {{
                    return typeof customElements !== 'undefined' && {checks};
                }}""",
                timeout=timeout
            )
            
            logger.debug(f"Web components {components} are ready")
            
        except Exception as e:
            raise WebComponentError(
                message=f"Timeout waiting for web components: {components}",
                component=str(components),
                details={'timeout': timeout, 'error': str(e)}
            )
            
    async def wait_for_shadow_root(
        self,
        selector: str,
        timeout: int = 30000
    ) -> None:
        """
        Wait for an element's shadow root to be available.
        
        Args:
            selector: Element selector
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            WebComponentError: If shadow root is not available within timeout
        """
        try:
            await self.page.wait_for_function(
                """(selector) => {
                    const el = document.querySelector(selector);
                    return el && el.shadowRoot;
                }""",
                arg=selector,
                timeout=timeout
            )
            
            logger.debug(f"Shadow root ready for {selector}")
            
        except Exception as e:
            raise WebComponentError(
                message=f"Timeout waiting for shadow root: {selector}",
                component=selector,
                details={'timeout': timeout, 'error': str(e)}
            )
            
    async def get_component_info(self, selector: str) -> Dict[str, Any]:
        """
        Get detailed information about a web component.
        
        Args:
            selector: Element selector
            
        Returns:
            Dictionary containing component information
            
        Raises:
            WebComponentError: If component information cannot be retrieved
        """
        try:
            info = await self.page.evaluate("""(selector) => {
                const el = document.querySelector(selector);
                if (!el) return null;
                
                return {
                    tagName: el.tagName.toLowerCase(),
                    defined: customElements.get(el.tagName.toLowerCase()) !== undefined,
                    properties: Object.getOwnPropertyNames(el),
                    attributes: Object.fromEntries(
                        Array.from(el.attributes).map(attr => [attr.name, attr.value])
                    ),
                    hasShadowRoot: !!el.shadowRoot,
                    shadowInfo: el.shadowRoot ? {
                        mode: el.shadowRoot.mode,
                        childCount: el.shadowRoot.childNodes.length,
                        elements: Array.from(el.shadowRoot.querySelectorAll('*')).map(node => ({
                            tagName: node.tagName.toLowerCase(),
                            id: node.id,
                            className: node.className
                        }))
                    } : null
                };
            }""", selector)
            
            if not info:
                raise WebComponentError(
                    message=f"Component not found: {selector}",
                    component=selector
                )
                
            logger.debug(f"Retrieved component info for {selector}: {info}")
            return info
            
        except Exception as e:
            raise WebComponentError(
                message=f"Failed to get component info: {selector}",
                component=selector,
                details={'error': str(e)}
            )
            
    async def find_components_by_type(
        self,
        component_type: str
    ) -> List[Dict[str, Any]]:
        """
        Find all instances of a specific web component type.
        
        Args:
            component_type: The component tag name to search for
            
        Returns:
            List of component information dictionaries
        """
        try:
            components = await self.page.evaluate("""(type) => {
                return Array.from(document.querySelectorAll(type)).map(el => ({
                    tagName: el.tagName.toLowerCase(),
                    id: el.id,
                    className: el.className,
                    attributes: Object.fromEntries(
                        Array.from(el.attributes).map(attr => [attr.name, attr.value])
                    ),
                    textContent: el.textContent?.trim() || '',
                    hasShadowRoot: !!el.shadowRoot,
                    rect: el.getBoundingClientRect().toJSON()
                }));
            }""", component_type)
            
            logger.debug(f"Found {len(components)} instances of {component_type}")
            return components
            
        except Exception as e:
            raise WebComponentError(
                message=f"Failed to find components of type: {component_type}",
                component=component_type,
                details={'error': str(e)}
            )