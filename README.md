# Browser Automation Extension for Goose

A browser automation extension for Goose that provides programmatic control of web browsers using Playwright.

## Features

- Launch and manage browser instances
- Navigate web pages
- Interact with page elements (click, type)
- Enhanced Google search functionality
- Advanced page inspection capabilities
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
python -m playwright install chromium
```

## Usage with Goose

1. Go to Settings > Extensions > Add
2. Set Type to StandardIO
3. Set Command to the full path of the browser-automation executable
4. Enable the extension

## Available Tools

### launch_browser
Launch a new browser instance
```python
params = {
    "headless": False  # Optional, default: False
}
```

### google_search
Perform a Google search with enhanced result handling
```python
params = {
    "query": "search term",          # Required: Search query
    "click_index": 1,               # Optional: Click nth result (1-based)
    "click_text": "Example.com",    # Optional: Click result containing text
    "ensure_visible": True          # Optional: Ensure result visible before click
}

# Returns:
{
    "success": True,
    "message": "Search completed successfully",
    "clicked": True,                # Whether a result was clicked
    "results": ["Title 1", ...]     # List of result titles
}
```

### navigate_to
Navigate to a URL
```python
params = {
    "url": "https://example.com",  # Required: Valid URL
    "wait_for": "networkidle"      # Optional: Wait state (load|domcontentloaded|networkidle)
}
```

### type_text
Type text into an element
```python
params = {
    "selector": "#search-input",   # Required: CSS selector
    "text": "example",            # Required: Text to type
    "submit": False              # Optional: Press Enter after typing
}
```

### click_element
Click an element with improved reliability
```python
params = {
    "selector": "#submit-button",  # Required: CSS selector
    "ensure_visible": True         # Optional: Ensure element in viewport
}
```

### inspect_page
Get current page state with configurable inspection options
```python
params = {
    "selector": "body",           # Optional: Element to start inspection from
    "max_elements": 100,          # Optional: Maximum elements to return
    "element_types": ["a", "button"], # Optional: Filter by element types
    "attributes": ["href", "class"],  # Optional: Attributes to include
    "max_depth": 3,              # Optional: Maximum depth to traverse
    "mode": "all"               # Optional: 'all', 'clickable', or 'form'
}

# Returns structured information about:
{
    "url": "current_url",
    "title": "page_title",
    "timestamp": "iso_timestamp",
    "viewport": {
        "width": 1280,
        "height": 800
    },
    "elements": [
        {
            "tag": "button",
            "id": "submit",
            "text": "Submit",
            "attributes": {...},
            "isVisible": true,
            "position": {
                "x": 100,
                "y": 200,
                "width": 80,
                "height": 40,
                "inViewport": true
            }
        }
    ],
    "totalElements": 10
}
```

### close_browser
Close the current browser instance
```python
params = {}  # No parameters required
```

## Best Practices

### Page Inspection
Use the appropriate inspection mode for your needs:
- `mode: "all"` - Full page structure with filtering
- `mode: "clickable"` - Focus on interactive elements
- `mode: "form"` - Focus on form inputs and controls

Example usage:
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

### Google Search Automation
Always use the `google_search()` function for Google searches rather than manually navigating and typing. This ensures:
- Reliable selectors are used
- Dynamic content is handled properly
- Results are waited for appropriately
- Multiple ways to click results

Example usage:
```python
# Basic search
result = await google_search({"query": "Block Inc"})

# Search and click first result
result = await google_search({
    "query": "Block Inc",
    "click_index": 1
})

# Search and click specific result
result = await google_search({
    "query": "Block Inc",
    "click_text": "Block, Inc. - Wikipedia"
})
```

### Element Interaction
- Always wait for elements to be ready before interacting
- Use `ensure_visible: true` when clicking elements
- Check return values for success/failure
- Use the inspector for debugging

## Error Handling

The extension provides detailed error information:

```python
{
    "error": {
        "code": ERROR_CODE,
        "message": "Human readable message"
    }
}
```

Common error codes:
- INVALID_PARAMS: Invalid or missing parameters
- INTERNAL_ERROR: Unexpected error during operation
- BROWSER_ERROR: Browser-related error
- NAVIGATION_ERROR: Failed to navigate
- ELEMENT_ERROR: Element interaction failed
- TIMEOUT_ERROR: Operation timed out

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
mcp dev src/browser_automation/server.py
```

4. Visit http://localhost:5173 to use the MCP Inspector

## Security

- URLs are validated before navigation
- Browser contexts are isolated
- Automatic cleanup of inactive sessions
- Input validation for all parameters
- Rate limiting for API requests

## Performance

- Automatic cleanup of inactive browser sessions
- Resource monitoring through status endpoint
- Configurable timeouts for operations
- Efficient selector strategies
- Memory-efficient page inspection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and linting
4. Submit a pull request

## License

MIT License