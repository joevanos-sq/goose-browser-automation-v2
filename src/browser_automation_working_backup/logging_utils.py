"""Advanced logging and debugging utilities for browser automation."""
import os
import sys
import time
import json
import logging
import platform
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from functools import wraps
from contextlib import contextmanager

# Configure logging directory
LOG_DIR = Path.home() / '.goose' / 'logs' / 'browser_automation'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Create log file with timestamp
LOG_FILE = LOG_DIR / f'browser_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
DEBUG_LOG = LOG_DIR / f'debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
TRACE_LOG = LOG_DIR / f'trace_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Configure logging formats
MAIN_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DEBUG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s'
TRACE_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s'

def setup_logging(debug: bool = False) -> None:
    """Configure logging with multiple handlers and formats."""
    # Create handlers
    main_handler = logging.FileHandler(LOG_FILE)
    debug_handler = logging.FileHandler(DEBUG_LOG)
    trace_handler = logging.FileHandler(TRACE_LOG)
    console_handler = logging.StreamHandler(sys.stdout)

    # Set formats
    main_handler.setFormatter(logging.Formatter(MAIN_FORMAT))
    debug_handler.setFormatter(logging.Formatter(DEBUG_FORMAT))
    trace_handler.setFormatter(logging.Formatter(TRACE_FORMAT))
    console_handler.setFormatter(logging.Formatter(MAIN_FORMAT))

    # Set levels
    main_handler.setLevel(logging.INFO)
    debug_handler.setLevel(logging.DEBUG)
    trace_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO if not debug else logging.DEBUG)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Add handlers
    root_logger.addHandler(main_handler)
    root_logger.addHandler(debug_handler)
    root_logger.addHandler(trace_handler)
    root_logger.addHandler(console_handler)

    # Log system information
    log_system_info()

def log_system_info() -> None:
    """Log detailed system information."""
    logger = logging.getLogger('system_info')
    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'python_path': sys.executable,
        'cwd': os.getcwd(),
        'env_vars': {k: v for k, v in os.environ.items() if 'SECRET' not in k.upper()},
        'timestamp': datetime.now().isoformat(),
    }
    logger.info(f"System Information:\n{json.dumps(info, indent=2)}")

class PerformanceMonitor:
    """Monitor and log performance metrics."""
    def __init__(self):
        self.logger = logging.getLogger('performance')
        self.start_time = time.time()
        self.checkpoints = []

    def checkpoint(self, name: str) -> None:
        """Record a timing checkpoint."""
        current_time = time.time()
        elapsed = current_time - self.start_time
        self.checkpoints.append((name, elapsed))
        self.logger.debug(f"Checkpoint '{name}': {elapsed:.3f}s")

    def summary(self) -> Dict[str, float]:
        """Get performance summary."""
        summary = {
            'total_time': time.time() - self.start_time,
            'checkpoints': {name: time for name, time in self.checkpoints}
        }
        self.logger.info(f"Performance Summary:\n{json.dumps(summary, indent=2)}")
        return summary

def log_exceptions(logger: Optional[logging.Logger] = None):
    """Decorator to log exceptions with full stack trace."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}\n"
                    f"Args: {args}, Kwargs: {kwargs}\n"
                    f"Stack trace:\n{traceback.format_exc()}"
                )
                raise
        return wrapper
    return decorator

class MCPLogger:
    """Log MCP protocol communication."""
    def __init__(self):
        self.logger = logging.getLogger('mcp')

    def log_request(self, request: Dict[str, Any]) -> None:
        """Log MCP request."""
        self.logger.debug(f"MCP Request:\n{json.dumps(request, indent=2)}")

    def log_response(self, response: Dict[str, Any]) -> None:
        """Log MCP response."""
        self.logger.debug(f"MCP Response:\n{json.dumps(response, indent=2)}")

    def log_error(self, error: Dict[str, Any]) -> None:
        """Log MCP error."""
        self.logger.error(f"MCP Error:\n{json.dumps(error, indent=2)}")

class PlaywrightLogger:
    """Log Playwright events and actions."""
    def __init__(self):
        self.logger = logging.getLogger('playwright')

    async def setup_page_logging(self, page) -> None:
        """Set up page event logging."""
        page.on('console', lambda msg: self.logger.debug(f'Console {msg.type}: {msg.text}'))
        page.on('pageerror', lambda err: self.logger.error(f'Page error: {err}'))
        page.on('request', lambda request: self.logger.debug(f'Request: {request.method} {request.url}'))
        page.on('response', lambda response: self.logger.debug(
            f'Response: {response.status} {response.url}'
        ))

    def log_action(self, action: str, selector: str, value: Optional[str] = None) -> None:
        """Log Playwright action."""
        msg = f"Action: {action}, Selector: {selector}"
        if value:
            msg += f", Value: {value}"
        self.logger.debug(msg)

@contextmanager
def log_operation(name: str):
    """Context manager to log operation timing."""
    logger = logging.getLogger('operations')
    start_time = time.time()
    logger.debug(f"Starting operation: {name}")
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.debug(f"Completed operation: {name} in {elapsed:.3f}s")