"""Enhanced page inspection utilities."""
import json
import logging
from typing import Dict, Any, List
from playwright.async_api import Page, Locator

class EnhancedInspector:
    """Enhanced page inspection utilities."""
    
    def __init__(self, page: Page):
        self.page = page
        
    async def inspect_element(self, selector: str) -> Dict[str, Any]:
        """Inspect a specific element in detail."""
        try:
            return await self.page.evaluate(f"""(selector) => {{
                const element = document.querySelector(selector);
                if (!element) return null;
                
                // Get computed styles
                const styles = window.getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                
                // Basic element info
                const info = {{
                    tagName: element.tagName.toLowerCase(),
                    id: element.id,
                    classes: Array.from(element.classList),
                    attributes: {{}},
                    styles: {{
                        display: styles.display,
                        visibility: styles.visibility,
                        opacity: styles.opacity,
                        position: styles.position,
                        zIndex: styles.zIndex
                    }},
                    geometry: {{
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        isVisible: rect.width > 0 && rect.height > 0
                    }},
                    isEnabled: !element.disabled,
                    isClickable: element.tagName === 'BUTTON' || 
                               element.tagName === 'A' ||
                               element.role === 'button',
                    textContent: element.textContent?.trim() || '',
                    innerHTML: element.innerHTML,
                    outerHTML: element.outerHTML,
                    hasShadowRoot: !!element.shadowRoot
                }};
                
                // Get all attributes
                for (const attr of element.attributes) {{
                    info.attributes[attr.name] = attr.value;
                }}
                
                // Check if element is actually visible
                info.isVisible = (
                    info.styles.display !== 'none' &&
                    info.styles.visibility !== 'hidden' &&
                    info.styles.opacity !== '0' &&
                    info.geometry.isVisible
                );
                
                // Check if element is in viewport
                const viewportHeight = window.innerHeight;
                const viewportWidth = window.innerWidth;
                info.isInViewport = (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= viewportHeight &&
                    rect.right <= viewportWidth
                );
                
                // Get shadow root info if available
                if (info.hasShadowRoot) {{
                    const shadowRoot = element.shadowRoot;
                    info.shadowRoot = {{
                        mode: shadowRoot.mode,
                        innerHTML: shadowRoot.innerHTML,
                        childNodes: Array.from(shadowRoot.childNodes).map(node => ({{
                            type: node.nodeType,
                            nodeName: node.nodeName,
                            textContent: node.textContent?.trim() || ''
                        }}))
                    }};
                }}
                
                // Get web component info
                if (element.tagName.includes('-')) {{
                    info.isWebComponent = true;
                    info.webComponentInfo = {{
                        defined: customElements.get(element.tagName.toLowerCase()) !== undefined,
                        properties: Object.getOwnPropertyNames(element)
                    }};
                }}
                
                return info;
            }}, selector""")
            
        except Exception as e:
            logging.error(f"Error inspecting element {selector}: {str(e)}")
            return None
            
    async def find_clickable_elements(self) -> List[Dict[str, Any]]:
        """Find all potentially clickable elements on the page."""
        try:
            return await self.page.evaluate("""() => {
                function isVisible(element) {
                    const rect = element.getBoundingClientRect();
                    const styles = window.getComputedStyle(element);
                    return (
                        rect.width > 0 &&
                        rect.height > 0 &&
                        styles.display !== 'none' &&
                        styles.visibility !== 'hidden' &&
                        styles.opacity !== '0'
                    );
                }
                
                function getElementInfo(element) {
                    const rect = element.getBoundingClientRect();
                    return {
                        tagName: element.tagName.toLowerCase(),
                        id: element.id,
                        classes: Array.from(element.classList),
                        attributes: Object.fromEntries(
                            Array.from(element.attributes).map(attr => [attr.name, attr.value])
                        ),
                        textContent: element.textContent?.trim() || '',
                        geometry: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        },
                        isWebComponent: element.tagName.includes('-'),
                        hasShadowRoot: !!element.shadowRoot
                    };
                }
                
                // Find all potentially clickable elements
                const clickableElements = [];
                
                // Regular DOM elements
                document.querySelectorAll('button, a, [role="button"], [data-testid*="button"], [data-test*="button"]')
                    .forEach(element => {
                        if (isVisible(element)) {
                            clickableElements.push(getElementInfo(element));
                        }
                    });
                
                // Web components
                document.querySelectorAll('market-button, market-link')
                    .forEach(element => {
                        if (isVisible(element)) {
                            clickableElements.push(getElementInfo(element));
                        }
                    });
                
                // Elements in shadow DOM
                document.querySelectorAll('*')
                    .forEach(element => {
                        if (element.shadowRoot) {
                            element.shadowRoot.querySelectorAll('button, a, [role="button"]')
                                .forEach(shadowElement => {
                                    if (isVisible(shadowElement)) {
                                        const info = getElementInfo(shadowElement);
                                        info.inShadowRoot = true;
                                        info.hostElement = getElementInfo(element);
                                        clickableElements.push(info);
                                    }
                                });
                        }
                    });
                
                return clickableElements;
            }""")
            
        except Exception as e:
            logging.error(f"Error finding clickable elements: {str(e)}")
            return []
            
    async def inspect_web_components(self) -> Dict[str, Any]:
        """Inspect web components on the page."""
        try:
            return await self.page.evaluate("""() => {
                const components = {};
                
                // Find all custom elements
                document.querySelectorAll('*')
                    .forEach(element => {
                        if (element.tagName.includes('-')) {
                            const tagName = element.tagName.toLowerCase();
                            if (!components[tagName]) {
                                components[tagName] = {
                                    count: 0,
                                    defined: customElements.get(tagName) !== undefined,
                                    instances: [],
                                    properties: Object.getOwnPropertyNames(element)
                                };
                            }
                            
                            components[tagName].count++;
                            components[tagName].instances.push({
                                id: element.id,
                                classes: Array.from(element.classList),
                                attributes: Object.fromEntries(
                                    Array.from(element.attributes).map(attr => [attr.name, attr.value])
                                ),
                                hasShadowRoot: !!element.shadowRoot,
                                textContent: element.textContent?.trim() || ''
                            });
                        }
                    });
                    
                return components;
            }""")
            
        except Exception as e:
            logging.error(f"Error inspecting web components: {str(e)}")
            return {}