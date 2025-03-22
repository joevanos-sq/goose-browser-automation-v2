"""Test configuration and shared fixtures."""
import pytest
import asyncio
import logging
from pathlib import Path
from browser_automation.server import BrowserAutomation, mcp

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / '.goose' / 'logs' / 'browser_automation_test.log')
    ]
)

@pytest.fixture
async def browser():
    """Provide a browser automation instance for tests."""
    automation = BrowserAutomation(debug=True)
    yield automation
    await automation.close()

@pytest.fixture
async def mcp_server():
    """Provide MCP server instance for tests."""
    return mcp

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()