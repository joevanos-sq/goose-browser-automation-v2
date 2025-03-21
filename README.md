# Web Automation Extension for Goose

A browser automation extension for Goose that provides programmatic control of web browsers using Playwright.

## Features

- Launch and manage browser instances
- Navigate web pages
- Interact with page elements (click, type)
- Support for both visible and headless browsers
- Automatic resource cleanup
- Comprehensive error handling
- Full async support

## Installation

1. Install the package:
```bash
uv pip install .
```

2. Install browser drivers (first time only):
```bash
python -m playwright install
```

## Usage with Goose

1. Go to Settings > Extensions > Add
2. Set Type to StandardIO
3. Set Command to the full path of the webautomation executable
4. Enable the extension

## Available Tools

### open_browser
Launch a new browser instance
```python
params = {
    "headless": False  # Optional, default: False
}
```

### navigate_to
Navigate to a URL
```python
params = {
    "browser_id": 1,  # Required: ID from open_browser
    "url": "https://example.com"  # Required: Valid URL
}
```

### click_element
Click an element on the page
```python
params = {
    "browser_id": 1,  # Required: Browser ID
    "selector": "#submit-button"  # Required: CSS selector
}
```

### input_text
Type text into a form field
```python
params = {
    "browser_id": 1,  # Required: Browser ID
    "selector": "#username",  # Required: CSS selector
    "text": "example"  # Required: Text to type
}
```

### close_browser
Close a browser instance
```python
params = {
    "browser_id": 1  # Required: Browser ID
}
```

## Error Handling

The extension provides detailed error information:

```python
{
    "error": {
        "type": "ERROR_TYPE",
        "message": "Human readable message",
        "details": {
            "error": "Original error message",
            "context": "Additional context"
        }
    }
}
```

Error types:
- BROWSER_NOT_FOUND
- PAGE_NOT_FOUND
- ELEMENT_NOT_FOUND
- NAVIGATION_FAILED
- INTERACTION_FAILED
- BROWSER_ERROR
- INVALID_INPUT
- TIMEOUT
- SECURITY_ERROR

## Development

1. Set up development environment:
```bash
uv sync
```

2. Run tests:
```bash
pytest
```

3. Run in development mode:
```bash
mcp dev src/webautomation/server.py
```

4. Visit http://localhost:5173 to use the MCP Inspector

## Security

- All URLs are validated before navigation
- Browser contexts are isolated
- Automatic cleanup of inactive sessions
- Input validation for all parameters

## Performance

- Automatic cleanup of inactive browser sessions (1 hour timeout)
- Resource monitoring through status endpoint
- Configurable timeouts for operations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and linting
4. Submit a pull request

## License

MIT License