"""Element inspection and debugging utilities."""
import json
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class ElementInspector:
    """Utility class for inspecting page elements."""
    
    def __init__(self, page: Page):
        """Initialize with Playwright page object."""
        self.page = page
    
    async def inspect_page(self, 
                         selector: str = 'body',
                         max_elements: int = 100,
                         element_types: Optional[List[str]] = None,
                         attributes: Optional[List[str]] = None,
                         max_depth: int = 3) -> Dict[str, Any]:
        """
        Analyze page structure with configurable limits and filters.
        
        Args:
            selector: Base selector to start inspection from
            max_elements: Maximum number of elements to return
            element_types: List of element types to include (e.g. ['a', 'button'])
            attributes: List of attributes to include in results
            max_depth: Maximum depth to traverse in DOM tree
            
        Returns:
            Dict containing filtered page analysis
        """
        # Create a params object to pass to JavaScript
        params = {
            "selector": selector,
            "maxElements": max_elements,
            "elementTypes": element_types or ['*'],
            "attributes": attributes or ['class', 'href', 'src', 'alt', 'title', 'role', 'aria-label'],
            "maxDepth": max_depth
        }
        
        script = """
        (params) => {
            const {selector, maxElements, elementTypes, attributes, maxDepth} = params;
            let elementCount = 0;
            
            function analyzeElement(element, depth = 0) {
                if (elementCount >= maxElements || depth >= maxDepth) {
                    return null;
                }
                
                if (elementTypes && !elementTypes.includes('*') && 
                    !elementTypes.includes(element.tagName.toLowerCase())) {
                    return null;
                }
                
                elementCount++;
                
                const info = {
                    tag: element.tagName.toLowerCase(),
                    id: element.id || null,
                    text: element.textContent?.trim()?.slice(0, 100) || null,
                };
                
                if (attributes && attributes.length > 0) {
                    info.attributes = {};
                    for (const attr of element.attributes) {
                        if (attributes.includes(attr.name)) {
                            info.attributes[attr.name] = attr.value;
                        }
                    }
                }
                
                info.isVisible = !(
                    element.style.display === 'none' || 
                    element.style.visibility === 'hidden' ||
                    element.style.opacity === '0' ||
                    element.offsetParent === null
                );
                
                if (info.isVisible) {
                    const rect = element.getBoundingClientRect();
                    info.position = {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        inViewport: (
                            rect.top >= 0 &&
                            rect.left >= 0 &&
                            rect.bottom <= window.innerHeight &&
                            rect.right <= window.innerWidth
                        )
                    };
                }
                
                if (depth < maxDepth) {
                    const children = [];
                    for (const child of element.children) {
                        const childInfo = analyzeElement(child, depth + 1);
                        if (childInfo) {
                            children.push(childInfo);
                        }
                    }
                    if (children.length > 0) {
                        info.children = children;
                    }
                }
                
                return info;
            }
            
            const root = document.querySelector(selector);
            if (!root) {
                return { error: `Element not found: ${selector}` };
            }
            
            return {
                url: window.location.href,
                title: document.title,
                timestamp: new Date().toISOString(),
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                elements: analyzeElement(root),
                totalElements: elementCount,
                filters: {
                    selector,
                    maxElements,
                    elementTypes: elementTypes || ['*'],
                    attributes: attributes || [],
                    maxDepth
                }
            };
        }
        """
        
        try:
            # Pass parameters as a single object
            result = await self.page.evaluate(script, params)
            
            if 'error' in result:
                logger.error(f"Page analysis error: {result['error']}")
            else:
                logger.debug(f"Analyzed {result['totalElements']} elements")
                
            return result
            
        except Exception as e:
            logger.error(f"Page analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def find_clickable_elements(self, max_elements: int = 50) -> Dict[str, Any]:
        """
        Find all clickable elements on the page.
        
        Args:
            max_elements: Maximum number of elements to return
            
        Returns:
            Dict containing clickable elements info
        """
        params = {"maxElements": max_elements}
        
        script = """
        (params) => {
            const {maxElements} = params;
            const clickableElements = [];
            let elementCount = 0;
            
            const clickableSelectors = [
                'a', 'button', 'input[type="submit"]', 'input[type="button"]',
                '[role="button"]', '[onclick]', '[class*="btn"]', '[class*="button"]'
            ];
            
            function isVisible(element) {
                return !!(
                    element.offsetWidth || 
                    element.offsetHeight || 
                    element.getClientRects().length
                ) && window.getComputedStyle(element).visibility !== 'hidden';
            }
            
            const elements = document.querySelectorAll(clickableSelectors.join(','));
            
            for (const element of elements) {
                if (elementCount >= maxElements) break;
                
                if (isVisible(element)) {
                    const rect = element.getBoundingClientRect();
                    
                    if (rect.width > 0 && rect.height > 0) {
                        elementCount++;
                        clickableElements.push({
                            tag: element.tagName.toLowerCase(),
                            id: element.id || null,
                            text: element.textContent?.trim()?.slice(0, 100) || null,
                            attributes: {
                                class: element.className,
                                href: element.href,
                                role: element.getAttribute('role'),
                                'aria-label': element.getAttribute('aria-label')
                            },
                            position: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height,
                                inViewport: (
                                    rect.top >= 0 &&
                                    rect.left >= 0 &&
                                    rect.bottom <= window.innerHeight &&
                                    rect.right <= window.innerWidth
                                )
                            }
                        });
                    }
                }
            }
            
            return {
                url: window.location.href,
                timestamp: new Date().toISOString(),
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                elements: clickableElements,
                totalElements: elementCount
            };
        }
        """
        
        try:
            result = await self.page.evaluate(script, params)
            logger.debug(f"Found {result['totalElements']} clickable elements")
            return result
            
        except Exception as e:
            logger.error(f"Failed to find clickable elements: {str(e)}")
            return {'error': str(e)}
    
    async def find_form_elements(self, max_elements: int = 50) -> Dict[str, Any]:
        """
        Find all form input elements on the page.
        
        Args:
            max_elements: Maximum number of elements to return
            
        Returns:
            Dict containing form elements info
        """
        params = {"maxElements": max_elements}
        
        script = """
        (params) => {
            const {maxElements} = params;
            const formElements = [];
            let elementCount = 0;
            
            const formSelectors = [
                'input:not([type="hidden"])',
                'textarea',
                'select',
                '[role="textbox"]',
                '[role="combobox"]',
                '[role="listbox"]',
                '[contenteditable="true"]'
            ];
            
            function isVisible(element) {
                return !!(
                    element.offsetWidth || 
                    element.offsetHeight || 
                    element.getClientRects().length
                ) && window.getComputedStyle(element).visibility !== 'hidden';
            }
            
            const elements = document.querySelectorAll(formSelectors.join(','));
            
            for (const element of elements) {
                if (elementCount >= maxElements) break;
                
                if (isVisible(element)) {
                    const rect = element.getBoundingClientRect();
                    
                    if (rect.width > 0 && rect.height > 0) {
                        elementCount++;
                        formElements.push({
                            tag: element.tagName.toLowerCase(),
                            type: element.type || null,
                            id: element.id || null,
                            name: element.name || null,
                            placeholder: element.placeholder || null,
                            label: (() => {
                                if (element.id) {
                                    const label = document.querySelector(`label[for="${element.id}"]`);
                                    if (label) return label.textContent.trim();
                                }
                                return element.getAttribute('aria-label');
                            })(),
                            attributes: {
                                required: element.required || false,
                                readonly: element.readOnly || false,
                                disabled: element.disabled || false,
                                'aria-required': element.getAttribute('aria-required'),
                                role: element.getAttribute('role')
                            },
                            position: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height,
                                inViewport: (
                                    rect.top >= 0 &&
                                    rect.left >= 0 &&
                                    rect.bottom <= window.innerHeight &&
                                    rect.right <= window.innerWidth
                                )
                            }
                        });
                    }
                }
            }
            
            return {
                url: window.location.href,
                timestamp: new Date().toISOString(),
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                elements: formElements,
                totalElements: elementCount
            };
        }
        """
        
        try:
            result = await self.page.evaluate(script, params)
            logger.debug(f"Found {result['totalElements']} form elements")
            return result
            
        except Exception as e:
            logger.error(f"Failed to find form elements: {str(e)}")
            return {'error': str(e)}