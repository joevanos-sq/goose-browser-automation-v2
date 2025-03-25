"""Smart selector strategies for dynamic web content."""
from typing import List, Dict, Any, Optional
import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)

class SmartSelector:
    """Dynamic selector builder with multiple strategies."""
    
    def __init__(self, page: Page):
        """Initialize with Playwright page object."""
        self.page = page
        
    async def find_best_selector(self, 
                               target_text: Optional[str] = None,
                               target_index: Optional[int] = None,
                               element_type: Optional[str] = None,
                               context: str = "document",
                               attributes: Optional[List[str]] = None) -> str:
        """
        Find the most reliable selector for an element based on context.
        
        Args:
            target_text: Text content to match
            target_index: Index of the element (1-based)
            element_type: Type of element to look for (e.g., 'link', 'button')
            context: Context to search in (e.g., 'search-results', 'navigation')
            
        Returns:
            Most reliable CSS selector for the element
        """
        # Get candidate elements based on initial criteria
        candidates = await self._find_candidate_elements(
            target_text, target_index, element_type, context, attributes
        )
        
        if not candidates:
            logger.debug(f"No candidates found for text={target_text}, index={target_index}")
            return None
            
        # Generate selector strategies for each candidate
        selectors = []
        for candidate in candidates:
            selector_strategies = await self._generate_selector_strategies(candidate)
            selectors.extend(selector_strategies)
            
        # Test and rank selectors
        best_selector = await self._find_most_reliable_selector(selectors)
        
        return best_selector
        
    async def _find_candidate_elements(self,
                                     target_text: Optional[str] = None,
                                     target_index: Optional[int] = None,
                                     element_type: Optional[str] = None,
                                     context: str = "document",
                                     attributes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Find elements matching the initial criteria."""
        # Use our inspection tool to get page elements
        inspection_params = {
            "max_elements": 20,  # Reasonable limit for performance
            "mode": "clickable" if element_type in ["link", "button"] else "all"
        }
        
        if context == "search-results":
            inspection_params["selector"] = "#search"
            
        # Get elements from the page
        elements = await self.page.evaluate("""
        (params) => {
            const findMatchingElements = () => {
                const matches = [];
                const elements = document.querySelectorAll('*');
                
                for (const el of elements) {
                    // Skip hidden elements
                    if (!el.offsetParent) continue;
                    
                    const text = el.textContent?.trim();
                    const isClickable = (
                        el.tagName === 'A' ||
                        el.tagName === 'BUTTON' ||
                        el.onclick ||
                        el.getAttribute('role') === 'button' ||
                        window.getComputedStyle(el).cursor === 'pointer'
                    );
                    
                    if (params.target_text && !text?.includes(params.target_text)) continue;
                    if (params.element_type === 'link' && el.tagName !== 'A') continue;
                    if (params.element_type === 'button' && !isClickable) continue;
                    
                    matches.push({
                        tag: el.tagName.toLowerCase(),
                        id: el.id,
                        classes: Array.from(el.classList),
                        attributes: Object.fromEntries(
                            Array.from(el.attributes)
                                .map(attr => [attr.name, attr.value])
                        ),
                        text: text,
                        isClickable,
                        position: el.getBoundingClientRect().toJSON()
                    });
                }
                return matches;
            };
            
            return findMatchingElements();
        }
        """, {"target_text": target_text, "element_type": element_type})
        
        # Filter by index if specified
        if target_index is not None and elements:
            elements = [elements[target_index - 1]] if 0 <= target_index - 1 < len(elements) else []
            
        return elements
        
    async def _generate_selector_strategies(self, element: Dict[str, Any]) -> List[str]:
        """Generate multiple possible selectors for an element."""
        selectors = []
        
        # Strategy 1: ID-based selector (most reliable)
        if element["id"]:
            selectors.append(f"#{element['id']}")
            
        # Strategy 2: Attribute-based selectors
        for name, value in element["attributes"].items():
            if name not in ["id", "class"] and value:
                # Handle special characters in attribute values
                value = value.replace('"', '\\"')
                selectors.append(f'{element["tag"]}[{name}="{value}"]')
                
        # Strategy 3: Class-based selectors
        if element["classes"]:
            class_selector = f'{element["tag"]}.{".".join(element["classes"])}'
            selectors.append(class_selector)
            
        # Strategy 4: Text-based selector
        if element["text"]:
            # Escape special characters in text
            text = element["text"].replace('"', '\\"')
            selectors.append(f'{element["tag"]}:has-text("{text}")')
            
        # Strategy 5: Position-based selector (last resort)
        if element["position"]:
            pos = element["position"]
            selectors.append(
                f'{element["tag"]}:where(not([style*="display: none"])'
                f':not([style*="visibility: hidden"])'
                f':not([style*="opacity: 0"])):nth-of-type({pos})'
            )
            
        return selectors
        
    async def _find_most_reliable_selector(self, selectors: List[str]) -> Optional[str]:
        """Test selectors and find the most reliable one."""
        if not selectors:
            return None
            
        best_selector = None
        best_score = -1
        
        for selector in selectors:
            try:
                # Test selector uniqueness
                elements = await self.page.query_selector_all(selector)
                if not elements:
                    continue
                    
                # Score the selector
                score = await self._score_selector(selector, len(elements))
                
                if score > best_score:
                    best_score = score
                    best_selector = selector
                    
            except Exception as e:
                logger.debug(f"Selector test failed for {selector}: {str(e)}")
                continue
                
        return best_selector
        
    async def _score_selector(self, selector: str, match_count: int) -> float:
        """
        Score a selector based on various factors.
        
        Factors considered:
        - Uniqueness (fewer matches is better)
        - Simplicity (shorter selectors preferred)
        - Reliability (ID > attributes > classes > position)
        - Visibility of matched elements
        """
        try:
            base_score = 100
            
            # Penalize for multiple matches
            if match_count > 1:
                base_score -= (match_count - 1) * 10
                
            # Bonus for ID-based selectors
            if selector.startswith('#'):
                base_score += 50
                
            # Penalty for complex selectors
            base_score -= selector.count(' ') * 5
            base_score -= selector.count('[') * 3
            
            # Check if element is visible
            is_visible = await self.page.evaluate(f"""
                selector => {{
                    const el = document.querySelector(selector);
                    if (!el) return false;
                    
                    const style = window.getComputedStyle(el);
                    return !!(
                        el.offsetWidth &&
                        el.offsetHeight &&
                        style.display !== 'none' &&
                        style.visibility !== 'hidden' &&
                        style.opacity !== '0'
                    );
                }}
            """, selector)
            
            if not is_visible:
                base_score -= 30
                
            return max(0, base_score)
            
        except Exception as e:
            logger.debug(f"Scoring failed for {selector}: {str(e)}")
            return 0
            
    async def find_element(self, 
                          target_text: Optional[str] = None,
                          target_index: Optional[int] = None,
                          element_type: Optional[str] = None,
                          context: str = "document",
                          attributes: Optional[List[str]] = None) -> Optional[Locator]:
        """
        Find an element using smart selector strategies.
        
        Args:
            target_text: Text content to match
            target_index: Index of the element (1-based)
            element_type: Type of element to look for (e.g., 'link', 'button')
            context: Context to search in (e.g., 'search-results', 'navigation')
            attributes: List of attributes to include in element analysis
            
        Returns:
            Playwright Locator for the element if found, None otherwise
        """
        selector = await self.find_best_selector(
            target_text=target_text,
            target_index=target_index,
            element_type=element_type,
            context=context,
            attributes=attributes
        )
        
        if not selector:
            return None
            
        return self.page.locator(selector)