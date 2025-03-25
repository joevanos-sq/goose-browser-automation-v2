"""Enhanced element inspection with selective analysis capabilities."""
import json
from typing import Dict, Any, List, Optional
from playwright.async_api import Page, ElementHandle

from browser_automation.utils.base_logger import BaseLogger

class EnhancedInspector(BaseLogger):
    """Advanced utility class for page inspection and element finding."""
    
    def __init__(self, page: Page):
        """Initialize inspector with page instance."""
        super().__init__()
        self.page = page
    
    async def find_interactive_element(self, options: Dict[str, Any]) -> Optional[ElementHandle]:
        """
        Find interactive element using multiple strategies.
        
        Args:
            options: {
                'text': Optional[str],       # Text content
                'role': Optional[str],       # ARIA role
                'position': Optional[int],   # nth element
                'near': Optional[str],       # Nearby element selector
                'attributes': Optional[Dict], # Required attributes
                'tag': Optional[str],        # HTML tag
                'timeout': Optional[int]     # Wait timeout
            }
        """
        self.info(f"Looking for element with options: {json.dumps(options)}")
        
        # Build composite selector using all available information
        selectors = await self._build_selectors(options)
        
        # Try each selector strategy
        for selector in selectors:
            try:
                self.debug(f"Trying selector: {selector}")
                element = await self.page.wait_for_selector(
                    selector,
                    state='visible',
                    timeout=options.get('timeout', 5000)
                )
                
                if element:
                    # Verify element state
                    state = await self.inspect_element_state(selector)
                    if state.get('clickable', False):
                        self.info(f"Found clickable element with selector: {selector}")
                        self.debug(f"Element state: {json.dumps(state, indent=2)}")
                        return element
                    else:
                        self.debug(f"Element found but not clickable: {selector}")
                        
            except Exception as e:
                self.debug(f"Selector {selector} failed: {str(e)}")
                continue
                
        return None
        
    async def _build_selectors(self, options: Dict[str, Any]) -> List[str]:
        """Build list of selectors in order of specificity."""
        selectors = []
        
        # Start with most specific combinations
        if options.get('text') and options.get('role'):
            selectors.extend([
                f'role={options["role"]}[text="{options["text"]}"]',
                f'[role="{options["role"]}"]:has-text("{options["text"]}")'
            ])
            
        # Add attribute-based selectors
        if options.get('attributes'):
            attr_str = ' and '.join(
                f'@{k}="{v}"' for k, v in options['attributes'].items()
            )
            selectors.append(f"//*[{attr_str}]")  # XPath for attributes
            
        # Add position-based selectors
        if options.get('position'):
            tag = options.get('tag', '*')
            pos = options['position']
            selectors.extend([
                f"{tag}:nth-of-type({pos})",
                f"//{tag}[{pos}]"  # XPath alternative
            ])
            
        # Add text-only selectors
        if options.get('text'):
            text = options['text']
            selectors.extend([
                f'text="{text}"',
                f'text=/{text}/i',
                f'[aria-label*="{text}"]'
            ])
            
        # Add role-only selectors
        if options.get('role'):
            selectors.append(f'[role="{options["role"]}"]')
            
        # Add relative position selectors
        if options.get('near'):
            near_selector = options['near']
            selectors.append(f'xpath=//*[following-sibling::*[1][{near_selector}]]')
            
        return selectors
    
    async def inspect_page(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze current page structure with configurable options.
        
        Args:
            options: Dictionary of inspection options:
                - max_inputs: int (default: 20)
                - max_components: int (default: 20)
                - max_attributes: int (default: 5)
                - text_length: int (default: 50)
                - include_inputs: bool (default: True)
                - include_components: bool (default: True)
        """
        options = options or {}
        script = f"""() => {{
            const CONFIG = {{
                maxInputs: {options.get('max_inputs', 20)},
                maxComponents: {options.get('max_components', 20)},
                maxAttributes: {options.get('max_attributes', 5)},
                textLength: {options.get('text_length', 50)},
                includeInputs: {str(options.get('include_inputs', True)).lower()},
                includeComponents: {str(options.get('include_components', True)).lower()}
            }};
            
            function truncateText(text, maxLength = CONFIG.textLength) {{
                if (!text) return '';
                return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
            }}
            
            function getElementInfo(element) {{
                const info = {{
                    tag: element.tagName.toLowerCase(),
                    id: element.id || '',
                    classes: Array.from(element.classList).slice(0, 5),
                    attributes: {{}},
                    isVisible: !(element.style.display === 'none' || 
                               element.style.visibility === 'hidden' ||
                               element.style.opacity === '0'),
                    textContent: truncateText(element.textContent)
                }};
                
                let attrCount = 0;
                for (const attr of element.attributes) {{
                    if (attrCount >= CONFIG.maxAttributes) break;
                    info.attributes[attr.name] = truncateText(attr.value);
                    attrCount++;
                }}
                
                return info;
            }}
            
            const result = {{
                url: window.location.href,
                title: truncateText(document.title),
                pageInfo: {{
                    headings: Array.from(document.querySelectorAll('h1, h2, h3'))
                        .slice(0, 10)
                        .map(h => ({{
                            level: h.tagName.toLowerCase(),
                            text: truncateText(h.textContent)
                        }}))
                }}
            }};
            
            if (CONFIG.includeInputs) {{
                result.inputs = Array.from(document.querySelectorAll('input, button, select, textarea'))
                    .slice(0, CONFIG.maxInputs)
                    .map(input => ({{
                        type: input.type || input.tagName.toLowerCase(),
                        id: input.id || '',
                        name: input.name || '',
                        placeholder: input.placeholder || '',
                        value: input.tagName.toLowerCase() === 'select' ? '' : (input.value || ''),
                        attributes: Object.fromEntries(
                            Array.from(input.attributes)
                                .slice(0, CONFIG.maxAttributes)
                                .map(attr => [attr.name, truncateText(attr.value)])
                        )
                    }}));
            }}
            
            if (CONFIG.includeComponents) {{
                result.webComponents = Array.from(document.querySelectorAll('*'))
                    .filter(el => el.tagName.includes('-'))
                    .slice(0, CONFIG.maxComponents)
                    .map(el => ({{
                        tag: el.tagName.toLowerCase(),
                        attributes: Object.fromEntries(
                            Array.from(el.attributes)
                                .slice(0, CONFIG.maxAttributes)
                                .map(attr => [attr.name, truncateText(attr.value)])
                        ),
                        hasShadowRoot: !!el.shadowRoot
                    }}));
            }}
            
            // Add basic form information
            result.forms = Array.from(document.forms)
                .slice(0, 5)
                .map(form => ({{
                    id: form.id || '',
                    name: form.name || '',
                    method: form.method || '',
                    action: truncateText(form.action || ''),
                    inputCount: form.elements.length
                }}));
            
            return result;
        }}"""
        
        try:
            result = await self.page.evaluate(script)
            self.debug("Enhanced Page Analysis Results:")
            self.debug(json.dumps(result, indent=2))
            return result
        except Exception as e:
            self.error(f"Enhanced page analysis failed: {str(e)}")
            return {}
    
    async def inspect_search_results(self) -> Dict[str, Any]:
        """Inspect Google search results with optimized parameters."""
        script = """() => {
            const results = Array.from(document.querySelectorAll('.g'))
                .slice(0, 10)  // Limit to first 10 results
                .map((result, index) => ({
                    position: index + 1,
                    title: result.querySelector('h3')?.textContent?.trim() || '',
                    url: result.querySelector('a')?.href || '',
                    snippet: result.querySelector('.VwiC3b')?.textContent?.trim()?.slice(0, 150) || ''
                }))
                .filter(r => r.title && r.url);  // Only include results with title and URL
                
            return {
                count: results.length,
                results: results,
                stats: {
                    totalResults: document.querySelector('#result-stats')?.textContent || '',
                    searchTime: document.querySelector('#search-stats')?.textContent || ''
                }
            };
        }"""
        
        try:
            result = await self.page.evaluate(script)
            self.debug("Search Results Analysis:")
            self.debug(json.dumps(result, indent=2))
            return result
        except Exception as e:
            self.error(f"Search results inspection failed: {str(e)}")
            return {"count": 0, "results": [], "stats": {}}
            
    async def inspect_element_state(self, selector: str) -> Dict[str, Any]:
        """Check detailed element state for debugging."""
        script = """(selector) => {
            const element = document.querySelector(selector);
            if (!element) return null;
            
            const rect = element.getBoundingClientRect();
            const computed = window.getComputedStyle(element);
            
            return {
                exists: true,
                visible: rect.height > 0 && rect.width > 0,
                inViewport: (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= window.innerHeight &&
                    rect.right <= window.innerWidth
                ),
                clickable: (
                    computed.pointerEvents !== 'none' &&
                    computed.visibility !== 'hidden' &&
                    computed.display !== 'none' &&
                    computed.opacity !== '0'
                ),
                position: {
                    top: rect.top,
                    left: rect.left,
                    bottom: rect.bottom,
                    right: rect.right
                },
                style: {
                    display: computed.display,
                    visibility: computed.visibility,
                    opacity: computed.opacity,
                    pointerEvents: computed.pointerEvents,
                    zIndex: computed.zIndex
                }
            };
        }"""
        
        try:
            result = await self.page.evaluate(script, selector)
            return result if result else {"exists": False}
        except Exception as e:
            self.error(f"Element state inspection failed: {str(e)}")
            return {"error": str(e)}