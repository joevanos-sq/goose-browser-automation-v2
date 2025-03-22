"""Logging utilities for browser automation."""
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

class DebugLogger:
    """Debug logging utility for browser automation."""
    
    def __init__(self):
        """Initialize debug logger."""
        # Create logs directory
        self.log_dir = Path.home() / '.goose/logs/browser_automation'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger('browser_automation')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        self.logger.handlers = []
        
        # Create handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Set up file and console handlers."""
        # File handler - debug level
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fh = logging.FileHandler(
            self.log_dir / f'automation_{timestamp}.log'
        )
        fh.setLevel(logging.DEBUG)
        
        # Console handler - info level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatter to handlers
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
    async def save_page_state(self, page, name: str):
        """
        Save complete page state for debugging.
        
        Args:
            page: Playwright page object
            name: Name prefix for saved files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{name}_{timestamp}"
        
        try:
            # Save screenshot
            screenshot_path = self.log_dir / f"{base_name}_screenshot.png"
            await page.screenshot(path=str(screenshot_path))
            
            # Save page content
            content_path = self.log_dir / f"{base_name}_content.html"
            content = await page.content()
            content_path.write_text(content)
            
            # Save page information
            info = {
                'url': page.url,
                'viewport': await page.viewport_size(),
                'timestamp': timestamp
            }
            
            # Add console logs if available
            console_logs = await page.evaluate("""() => {
                return window.consoleLog || [];
            }""")
            
            if console_logs:
                info['console_logs'] = console_logs
                
            # Save info
            info_path = self.log_dir / f"{base_name}_info.json"
            info_path.write_text(json.dumps(info, indent=2))
            
            self.logger.info(f"Page state saved: {base_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to save page state: {str(e)}")
            
    def get_latest_log(self) -> Optional[str]:
        """Get path to latest log file."""
        try:
            logs = list(self.log_dir.glob('automation_*.log'))
            if logs:
                return str(sorted(logs)[-1])
        except Exception as e:
            self.logger.error(f"Failed to get latest log: {str(e)}")
        return None