# Web Automation Extension Documentation

## Overview

The Web Automation Extension is a Goose extension designed to provide robust, reliable web automation capabilities with specific optimizations for web applications. It implements the Model Context Protocol (MCP) and uses Playwright for modern web automation.

## Architecture

### Core Components

1. **MCPServer**
   - Implements the MCP protocol interface
   - Handles JSON-RPC communication
   - Routes tool calls to appropriate handlers
   - Manages initialization and capability declaration

2. **BrowserController**
   - Manages browser instances and automation
   - Handles browser lifecycle (launch, interact, close)
   - Provides retry mechanisms and error handling
   - Implements selectors and interactions

3. **ElementInspector**
   - Provides detailed page analysis
   - Supports multiple inspection modes
   - Handles DOM traversal and filtering
   - Provides element visibility information

### Directory Structure
```
browser_automation/
├── src/
│   └── browser_automation/
│       ├── __init__.py
│       ├── server.py
│       ├── controllers/
│       │   ├── __init__.py
│       │   ├── browser_controller.py
│       │   └── square_controller.py
│       └── utils/
│           ├── __init__.py
│           ├── inspector.py
│           ├── selectors.py
│           └── base_logger.py
├── tests/
│   ├── integration/
│   │   └── test_square_login.py
│   └── unit/
│       └── test_browser.py
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

### 3. Page Inspection
- Multiple inspection modes:
  - Full page structure analysis
  - Clickable elements focus
  - Form elements focus
- Configurable filtering:
  - Element type filtering
  - Attribute selection
  - Depth control
- Visibility information:
  - Element dimensions
  - Viewport position
  - Visibility state
- Performance optimizations:
  - Element count limits
  - Selective attribute collection
  - Efficient DOM traversal

### 4. Error Handling & Debugging
- Comprehensive logging system
  - Location: ~/.goose/logs/browser_automation/
  - Format: Timestamped entries with context
  - Levels: DEBUG, INFO, WARNING, ERROR
- Playwright tracing for debugging
- Retry mechanism with exponential backoff
- Detailed error messages with context

### 5. Tools API

#### browser_automation__launch_browser
```python
{
    "name": "browser_automation__launch_browser",
    "parameters": {
        "headless": {
            "type": "boolean",
            "default": False
        }
    }
}
```

#### browser_automation__navigate_to
```python
{
    "name": "browser_automation__navigate_to",
    "parameters": {
        "url": "string",
        "wait_for": {
            "type": "string",
            "enum": ["load", "domcontentloaded", "networkidle"],
            "default": "networkidle"
        }
    }
}
```

#### browser_automation__inspect_page
```python
{
    "name": "browser_automation__inspect_page",
    "parameters": {
        "selector": {
            "type": "string",
            "default": "body"
        },
        "max_elements": {
            "type": "integer",
            "default": 100
        },
        "element_types": {
            "type": "array",
            "items": {"type": "string"},
            "optional": true
        },
        "attributes": {
            "type": "array",
            "items": {"type": "string"},
            "optional": true
        },
        "max_depth": {
            "type": "integer",
            "default": 3
        },
        "mode": {
            "type": "string",
            "enum": ["all", "clickable", "form"],
            "default": "all"
        }
    }
}
```

#### browser_automation__close_browser
```python
{
    "name": "browser_automation__close_browser",
    "parameters": {}
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

### 3. Inspection Architecture
```python
class ElementInspector:
    """
    Implements a flexible page inspection system with:
    - Multiple inspection modes
    - Configurable filtering
    - Performance optimization
    - Memory efficiency
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
   mcp = ">=1.4.0"
   ```

3. **System Requirements**
   - Chrome Canary installed
   - Write access to ~/.goose/logs
   - Network access for web automation

### Performance Requirements
1. **Response Times**
   - Tool execution < 30s
   - Browser launch < 5s
   - Element interaction < 1s
   - Page inspection < 2s

2. **Resource Usage**
   - Memory per browser < 500MB
   - Log file rotation
   - Automatic cleanup of old sessions
   - Efficient DOM traversal

## Extension Development

### Adding New Features
1. Update BrowserController with new functionality
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
DEBUG=1 python -m browser_automation
```

### Debugging
1. Check logs in ~/.goose/logs/browser_automation/
2. Use Playwright trace files
3. Enable debug logging
4. Use browser devtools in non-headless mode

## Common Usage Patterns

### Page Inspection
```python
# Get clickable elements
result = await inspect_page({
    "mode": "clickable",
    "max_elements": 10
})

# Get form elements
result = await inspect_page({
    "mode": "form",
    "max_elements": 5
})

# Get specific elements
result = await inspect_page({
    "element_types": ["a", "button"],
    "attributes": ["href", "class"],
    "max_depth": 2
})
```

## Future Enhancements
1. Visual element highlighting
2. Network request interception
3. Visual regression testing
4. Performance metrics collection
5. Extended component support

## Security Considerations
1. Input validation
2. Session isolation
3. Network security
4. Resource cleanup

This documentation provides a comprehensive overview of the extension's architecture, features, and usage. It serves as both a technical reference and a guide for future development.