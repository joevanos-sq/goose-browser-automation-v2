"""Test configuration and shared fixtures."""
import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from playwright.async_api import Page

from browser_automation.controllers.browser_controller import BrowserController

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / '.goose' / 'logs' / 'browser_automation_test.log')
    ]
)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def browser() -> AsyncGenerator[BrowserController, None]:
    """Provide a browser automation instance for tests."""
    controller = BrowserController()
    await controller.launch(headless=True)  # Use headless mode for tests
    yield controller
    await controller.close()

@pytest.fixture
async def browser_page(browser: BrowserController) -> AsyncGenerator[Page, None]:
    """Provide a browser page for tests."""
    if not browser.page:
        raise ValueError("Browser not launched")
    yield browser.page