# Web Automation Extension Documentation

## Overview

The Web Automation Extension is a Goose extension designed to provide robust, reliable web automation capabilities with specific optimizations for Square's web applications. It implements the Model Context Protocol (MCP) and uses Playwright for modern web automation.

## Architecture

### Core Components

1. **MCPServer**
   - Implements the MCP protocol interface
   - Handles JSON-RPC communication
   - Routes tool calls to appropriate handlers
   - Manages initialization and capability declaration

2. **PlaywrightManager**
   - Manages browser instances and automation
   - Handles browser lifecycle (launch, interact, close)
   - Provides retry mechanisms and error handling
   - Implements Square-specific selectors and interactions

### Directory Structure
```
webautomation/
├── src/
│   └── webautomation/
│       ├── __init__.py
│       ├── __main__.py
│       └── server.py
├── tests/
├── pyproject.toml
└── README.md
```

## Features

### 1. Browser Management
- Launch Chrome Canary instances
- Support for both headless and visible modes
- Multiple concurrent browser sessions
- Automatic resource cleanup
- Session persistence tracking

### 2. Web Interaction
- Navigation with network activity monitoring
- Element interaction (click, type, select)
- Shadow DOM support
- Frame handling
- Wait mechanisms for page loads and network idle

### 3. Square-Specific Features
- Specialized selectors for Square components:
  ```python
  SQUARE_COMPONENTS = {
      'market-button': 'market-button',
      'market-input-text': 'market-input-text',
      'market-select': 'market-select',
      'market-dropdown': 'market-dropdown',
      'sq-button': 'sq-button',
      'sq-input': 'sq-input',
      'sq-form': 'sq-form',
      'sq-payment-form': 'sq-payment-form'
  }
  ```
- Handling of Square's custom web components
- Support for Square's authentication flows
- Recognition of Square-specific data-testid attributes

### 4. Error Handling & Debugging
- Comprehensive logging system
  - Location: ~/.goose/logs/webautomation/
  - Format: Timestamped entries with context
  - Levels: DEBUG, INFO, WARNING, ERROR
- Playwright tracing for debugging
- Retry mechanism with exponential backoff
- Detailed error messages with context

### 5. Tools API

#### webautomation__launch_browser
```python
{
    "name": "webautomation__launch_browser",
    "parameters": {
        "headless": {
            "type": "boolean",
            "default": False
        }
    }
}
```

#### webautomation__navigate
```python
{
    "name": "webautomation__navigate",
    "parameters": {
        "browser_id": "integer",
        "url": "string"
    }
}
```

#### webautomation__interact
```python
{
    "name": "webautomation__interact",
    "parameters": {
        "browser_id": "integer",
        "action": "string",  # click, type, select
        "selector": "string",
        "value": "string"    # optional
    }
}
```

#### webautomation__close_browser
```python
{
    "name": "webautomation__close_browser",
    "parameters": {
        "browser_id": "integer"
    }
}
```

## Design Decisions

### 1. Why Playwright?
- Modern web automation capabilities
- Better handling of shadow DOM and web components
- Built-in support for modern JavaScript features
- Superior performance compared to Selenium
- Better stability and less flakiness

### 2. Why Chrome Canary?
- Latest Chrome features
- Better developer tools
- More consistent behavior with modern web apps
- Better support for web components

### 3. Retry Mechanism Design
```python
async def _retry_with_logging(self, func, max_retries=3, delay=1):
    """
    Implements exponential backoff with:
    - Detailed logging of each attempt
    - Configurable retry count and delay
    - Preservation of error context
    """
```

### 4. Logging Strategy
- Separate log file per session
- Structured logging with timestamps
- Both file and stdout logging
- Trace files for debugging

## Requirements

### Technical Requirements
1. **Python Environment**
   - Python 3.13+
   - Async/await support
   - Access to filesystem for logs

2. **Dependencies**
   ```toml
   [dependencies]
   playwright = ">=1.51.0"
   asyncio = "*"
   logging = "*"
   ```

3. **System Requirements**
   - Chrome Canary installed
   - Write access to ~/.goose/logs
   - Network access for web automation

### Functional Requirements
1. **Browser Control**
   - Launch/close browsers
   - Multiple concurrent sessions
   - Resource management

2. **Web Interaction**
   - Navigation
   - Element interaction
   - Shadow DOM support
   - Frame handling

3. **Square Integration**
   - Support for Square web components
   - Authentication flow handling
   - Custom selector support

4. **Error Handling**
   - Retry mechanisms
   - Logging
   - Debugging support

### Performance Requirements
1. **Response Times**
   - Tool execution < 30s
   - Browser launch < 5s
   - Element interaction < 1s

2. **Resource Usage**
   - Memory per browser < 500MB
   - Log file rotation
   - Automatic cleanup of old sessions

## Extension Development

### Adding New Features
1. Update PlaywrightManager with new functionality
2. Add new tool definition in MCPServer
3. Update documentation
4. Add tests

### Testing
```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run with debug logging
DEBUG=1 python -m webautomation
```

### Debugging
1. Check logs in ~/.goose/logs/webautomation/
2. Use Playwright trace files
3. Enable debug logging
4. Use browser devtools in non-headless mode

## Common Usage Patterns

### Square Login Flow
```python
# Launch browser
browser_id = webautomation__launch_browser(headless=False)

# Login sequence
webautomation__navigate(browser_id, "https://app.squareupstaging.com/login")
webautomation__interact(browser_id, "type", "market-input-text[data-testid='email-input']", "email@example.com")
webautomation__interact(browser_id, "click", "market-button[data-testid='continue-button']")
webautomation__interact(browser_id, "type", "market-input-text[data-testid='password-input']", "password")
webautomation__interact(browser_id, "click", "market-button[data-testid='sign-in-button']")
```

## Future Enhancements
1. Cookie/session management
2. Network request interception
3. Visual regression testing
4. Performance metrics collection
5. Extended Square component support

## Security Considerations
1. Credential handling
2. Session isolation
3. Network security
4. Resource cleanup

This documentation provides a comprehensive overview of the extension's architecture, features, and usage. It serves as both a technical reference and a guide for future development.