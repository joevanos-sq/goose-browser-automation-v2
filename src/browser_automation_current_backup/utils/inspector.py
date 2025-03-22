"""Element inspection and debugging utilities."""
import json
import logging
from typing import Dict, Any
from playwright.async_api import Page

class ElementInspector:
    """Utility class for inspecting page elements."""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def inspect_page(self) -> Dict[str, Any]:
        """Analyze current page structure."""
        script = """() => {
            function analyzeElement(element, depth = 0) {
                const info = {
                    tag: element.tagName.toLowerCase(),
                    id: element.id,
                    classes: Array.from(element.classList),
                    attributes: {},
                    hasShadowRoot: !!element.shadowRoot,
                    isVisible: !(element.style.display === 'none' || 
                               element.style.visibility === 'hidden' ||
                               element.style.opacity === '0'),
                    textContent: element.textContent.trim().slice(0, 50)
                };
                
                // Get all attributes
                for (const attr of element.attributes) {
                    info.attributes[attr.name] = attr.value;
                }
                
                return info;
            }
            
            // Get all inputs
            const inputs = Array.from(document.querySelectorAll('input')).map(input => ({
                type: input.type,
                id: input.id,
                name: input.name,
                attributes: Object.fromEntries(
                    Array.from(input.attributes).map(attr => [attr.name, attr.value])
                )
            }));
            
            // Get all web components
            const webComponents = Array.from(document.querySelectorAll('*'))
                .filter(el => el.tagName.includes('-'))
                .map(el => ({
                    tag: el.tagName.toLowerCase(),
                    attributes: Object.fromEntries(
                        Array.from(el.attributes).map(attr => [attr.name, attr.value])
                    ),
                    hasShadowRoot: !!el.shadowRoot
                }));
                
            return {
                url: window.location.href,
                title: document.title,
                inputs: inputs,
                webComponents: webComponents
            };
        }"""
        
        try:
            result = await self.page.evaluate(script)
            logging.debug("Page Analysis Results:")
            logging.debug(json.dumps(result, indent=2))
            return result
        except Exception as e:
            logging.error(f"Page analysis failed: {str(e)}")
            return {}
    
    async def find_all_inputs(self) -> Dict[str, Any]:
        """Find all input elements on the page."""
        script = """() => {
            function getInputInfo(input) {
                return {
                    type: input.type,
                    id: input.id,
                    name: input.name,
                    value: input.value,
                    isVisible: !(input.style.display === 'none' || 
                               input.style.visibility === 'hidden' ||
                               input.style.opacity === '0'),
                    attributes: Object.fromEntries(
                        Array.from(input.attributes).map(attr => [attr.name, attr.value])
                    ),
                    boundingBox: input.getBoundingClientRect()
                };
            }
            
            // Regular inputs
            const regularInputs = Array.from(document.querySelectorAll('input'))
                .map(getInputInfo);
            
            // Shadow DOM inputs
            const shadowInputs = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.shadowRoot) {
                    Array.from(el.shadowRoot.querySelectorAll('input'))
                        .forEach(input => shadowInputs.push(getInputInfo(input)));
                }
            });
            
            return {
                regularInputs,
                shadowInputs
            };
        }"""
        
        try:
            result = await self.page.evaluate(script)
            logging.debug("Input Analysis Results:")
            logging.debug(json.dumps(result, indent=2))
            return result
        except Exception as e:
            logging.error(f"Input analysis failed: {str(e)}")
            return {}