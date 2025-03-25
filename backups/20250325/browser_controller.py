"""Browser controller with Chromium support."""
from __future__ import annotations

import random
import json
from typing import Dict, Any, Optional, Literal, List, Tuple, cast
from playwright.async_api import async_playwright, Page, Browser, Playwright, TimeoutError, ElementHandle

from browser_automation.utils.selectors import GoogleSelectors
from browser_automation.utils.enhanced_inspector import EnhancedInspector
from browser_automation.utils.base_logger import BaseLogger

class BrowserController(BaseLogger):
    """Controls browser automation with Chromium."""
    
    def __init__(self) -> None:
        """Initialize the controller."""
        super().__init__('browser_controller')
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._inspector: Optional[EnhancedInspector] = None

    @property
    def page(self) -> Optional[Page]:
        """Get current page."""
        return self._page

    def _ensure_page(self) -> Page:
        """Ensure page exists and return it."""
        if not self._page:
            raise ValueError("Browser page not initialized")
        return self._page

    async def wait_for_element_ready(self, element: ElementHandle, ensure_visible: bool = True) -> bool:
        """
        Wait for an element to be ready for interaction.
        
        Args:
            element: Element to check
            ensure_visible: Whether to ensure element is in viewport
            
        Returns:
            bool: True if element is ready, False otherwise
        """
        try:
            page = self._ensure_page()
                
            # Check element state
            is_visible = await element.is_visible()
            is_enabled = await element.is_enabled()
            self.info(f"Element state - visible: {is_visible}, enabled: {is_enabled}")
            
            if not (is_visible and is_enabled):
                return False
                
            # Ensure element is in viewport if requested
            if ensure_visible:
                await element.scroll_into_view_if_needed()
                # Check if element is stable (no animations)
                try:
                    await element.wait_for_element_state('stable', timeout=5000)
                except Exception as e:
                    self.warning(f"Element may not be stable: {str(e)}")
                    return False
                
            # Check for overlays using JavaScript
            try:
                no_overlays = await page.evaluate("""(element) => {
                    const rect = element.getBoundingClientRect();
                    const center = {
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2
                    };
                    const elementAtPoint = document.elementFromPoint(center.x, center.y);
                    return element.contains(elementAtPoint) || element === elementAtPoint;
                }""", element)
                
                if not no_overlays:
                    self.warning("Element may be covered by overlay")
                    return False
            except Exception as e:
                self.warning(f"Could not check for overlays: {str(e)}")
                return False
                
            return True
            
        except Exception as e:
            self.error(f"Error checking element readiness: {str(e)}")
            return False

    async def _wait_for_page_ready(self) -> bool:
        """
        Wait for page to be fully ready.
        
        Returns:
            bool: True if page is ready, False otherwise
        """
        try:
            page = self._ensure_page()

            # Wait for network to be idle
            await page.wait_for_load_state("networkidle")
            
            # Check for loading indicators
            try:
                no_loading = await page.evaluate("""() => {
                    const loadingElements = document.querySelectorAll(
                        '[class*="loading"], [class*="spinner"], [class*="progress"]'
                    );
                    return loadingElements.length === 0;
                }""")
                if not no_loading:
                    return False
            except Exception as e:
                self.warning(f"Could not check loading indicators: {str(e)}")
                return False
            
            # Check for images
            try:
                images_loaded = await page.evaluate("""() => {
                    return Array.from(document.images).every((img) => img.complete);
                }""")
                if not images_loaded:
                    return False
            except Exception as e:
                self.warning(f"Could not check image loading: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            self.warning(f"Some elements still loading: {str(e)}")
            return False

    async def click_element(self, selector: str, ensure_visible: bool = True, timeout: int = 10000) -> bool:
        """
        Click on an element with improved reliability.
        
        Args:
            selector: Element selector
            ensure_visible: Whether to ensure element is in viewport
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            page = self._ensure_page()
            self.info(f"Attempting to click element: {selector}")
                
            # Wait for element with longer timeout
            element = await page.wait_for_selector(
                selector,
                state='visible',
                timeout=timeout
            )
            
            if not element:
                self.error(f"Element not found: {selector}")
                return False
                
            # Ensure element is ready
            if not await self.wait_for_element_ready(element, ensure_visible):
                self.error(f"Element not ready for interaction: {selector}")
                return False
                
            # Try clicking with retry
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Click with natural timing
                    await element.hover()  # More human-like
                    await element.click()
                    
                    # Wait for any navigation or network activity
                    await page.wait_for_load_state("networkidle", timeout=5000)
                    
                    self.info(f"Successfully clicked {selector} on attempt {attempt + 1}")
                    return True
                    
                except Exception as e:
                    if attempt == max_attempts - 1:
                        self.error(f"All click attempts failed: {str(e)}")
                        return False
                    self.warning(f"Click attempt {attempt + 1} failed, retrying...")
                    
                    # Check for overlays using JavaScript
                    try:
                        await page.evaluate("""() => {
                            const overlays = document.querySelectorAll('.overlay, .popup, .modal');
                            overlays.forEach(overlay => overlay.remove());
                            return true;
                        }""")
                    except Exception as e:
                        self.warning(f"Could not remove overlays: {str(e)}")
                        continue
                    
            return False
                    
        except ValueError as e:
            self.error(str(e))
            return False
        except Exception as e:
            self.error(f"Failed to click element: {str(e)}")
            return False