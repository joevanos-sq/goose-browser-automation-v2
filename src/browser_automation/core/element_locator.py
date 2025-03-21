"""Element location utilities."""
import logging
from typing import Optional, Dict, Any, List
from playwright.async_api import Page, Locator, TimeoutError
from .exceptions import ElementNotFoundError

logger = logging.getLogger(__name__)


class ElementLocator:
    """Flexible element location with multiple strategies."""
    
    def __init__(self, page: Page):
        """Initialize with a page instance."""
        self.page = page
        
    async def find_element(
        self,
        options: Dict[str, Any],
        timeout: int = 5000
    ) -> Locator:
        """
        Find an element using multiple strategies.
        
        Args:
            options: Dictionary with search options:
                - test_id: data-testid attribute value
                - text: Text content to match
                - role: ARIA role
                - tag: HTML tag or web component name
                - label: Label text (for form controls)
                - placeholder: Placeholder text
                - class_name: CSS class
            timeout: Maximum time to wait for element
            
        Returns:
            Playwright Locator object
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        strategies = [
            # Test ID strategy
            lambda: options.get('test_id') and
                self.page.locator(f'[data-testid="{options["test_id"]}"]'),
                
            # Text content strategy
            lambda: options.get('text') and
                self.page.locator(f'text="{options["text"]}"'),
                
            # Role strategy
            lambda: options.get('role') and
                self.page.locator(f'[role="{options["role"]}"]'),
                
            # Tag strategy
            lambda: options.get('tag') and
                self.page.locator(options['tag']),
                
            # Label strategy
            lambda: options.get('label') and
                self.page.locator(f'label:has-text("{options["label"]}")'),
                
            # Placeholder strategy
            lambda: options.get('placeholder') and
                self.page.locator(f'[placeholder="{options["placeholder"]}"]'),
                
            # Class strategy
            lambda: options.get('class_name') and
                self.page.locator(f'.{options["class_name"]}')
        ]
        
        errors = []
        for strategy in strategies:
            try:
                locator = strategy()
                if locator:
                    await locator.wait_for(
                        state='visible',
                        timeout=timeout
                    )
                    logger.debug(
                        f"Found element using options: {options}"
                    )
                    return locator
            except Exception as e:
                errors.append(str(e))
                continue
                
        raise ElementNotFoundError(
            message="Element not found with any strategy",
            selector=str(options),
            details={'errors': errors}
        )
        
    async def find_all_elements(
        self,
        options: Dict[str, Any],
        timeout: int = 5000
    ) -> List[Locator]:
        """
        Find all elements matching the criteria.
        
        Args:
            options: Same as find_element
            timeout: Maximum time to wait
            
        Returns:
            List of Playwright Locator objects
        """
        try:
            if options.get('test_id'):
                elements = await self.page.locator(
                    f'[data-testid="{options["test_id"]}"]'
                ).all()
            elif options.get('text'):
                elements = await self.page.locator(
                    f'text="{options["text"]}"'
                ).all()
            elif options.get('role'):
                elements = await self.page.locator(
                    f'[role="{options["role"]}"]'
                ).all()
            elif options.get('tag'):
                elements = await self.page.locator(
                    options['tag']
                ).all()
            else:
                raise ValueError("No valid search criteria provided")
                
            logger.debug(
                f"Found {len(elements)} elements with options: {options}"
            )
            return elements
            
        except Exception as e:
            raise ElementNotFoundError(
                message="Failed to find elements",
                selector=str(options),
                details={'error': str(e)}
            )
            
    async def wait_for_element(
        self,
        options: Dict[str, Any],
        state: str = 'visible',
        timeout: int = 30000
    ) -> Locator:
        """
        Wait for an element to reach a specific state.
        
        Args:
            options: Same as find_element
            state: State to wait for ('attached'|'detached'|'visible'|'hidden')
            timeout: Maximum time to wait
            
        Returns:
            Playwright Locator object
        """
        try:
            element = await self.find_element(options, timeout)
            await element.wait_for(
                state=state,
                timeout=timeout
            )
            logger.debug(
                f"Element reached state '{state}' with options: {options}"
            )
            return element
            
        except TimeoutError as e:
            raise ElementNotFoundError(
                message=f"Timeout waiting for element state: {state}",
                selector=str(options),
                details={'timeout': timeout, 'state': state}
            )
            
    async def is_element_present(
        self,
        options: Dict[str, Any],
        timeout: int = 1000
    ) -> bool:
        """
        Check if an element is present without throwing errors.
        
        Args:
            options: Same as find_element
            timeout: Maximum time to wait
            
        Returns:
            True if element is found, False otherwise
        """
        try:
            await self.find_element(options, timeout)
            return True
        except ElementNotFoundError:
            return False