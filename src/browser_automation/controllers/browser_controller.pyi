"""Type stub file for BrowserController."""
from typing import Dict, Any, Optional, Literal, List
from playwright.async_api import Page, Browser, Playwright, Locator

class BrowserController:
    _playwright: Optional[Playwright]
    _browser: Optional[Browser]
    _page: Optional[Page]

    def __init__(self) -> None: ...
    
    @property
    def page(self) -> Optional[Page]: ...

    async def launch(self, headless: bool = ...) -> bool: ...
    
    async def navigate(self, url: str, wait_for: Literal['load', 'domcontentloaded', 'networkidle'] = ...) -> bool: ...
    
    async def type_text(self, selector: str, text: str, submit: bool = ...) -> bool: ...
    
    async def click_element(self, selector: str, ensure_visible: bool = ...) -> bool: ...
    
    async def click_with_retry(self, selector: str, max_attempts: int = ..., delay: int = ..., ensure_visible: bool = ...) -> bool: ...
    
    async def inspect_page(self, 
                         selector: str = ...,
                         max_elements: int = ...,
                         element_types: Optional[List[str]] = ...,
                         attributes: Optional[List[str]] = ...,
                         max_depth: int = ...,
                         mode: Literal['all', 'clickable', 'form'] = ...) -> Dict[str, Any]: ...
    
    async def click_result_by_text(self, text: str, ensure_visible: bool = ..., allowed_types: List[str] = ...) -> bool: ...
    
    async def close(self) -> None: ...