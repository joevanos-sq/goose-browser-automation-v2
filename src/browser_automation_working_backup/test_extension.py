"""Test script for browser automation extension."""
import asyncio
import json
import sys
import signal
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def handle_sigint() -> Iterator[None]:
    """Handle SIGINT gracefully."""
    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original_handler)

async def test_extension():
    """Test the browser automation extension."""
    try:
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"},
                "protocolVersion": "1.0.0"
            }
        }
        
        # Send initialize request
        print(json.dumps(init_request), flush=True)
        
        # Read response
        response = json.loads(sys.stdin.readline())
        print("Initialize response:", response)
        
        # Send notification
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print(json.dumps(notification), flush=True)
        
        # Send tools/list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print(json.dumps(list_request), flush=True)
        
        # Read response
        response = json.loads(sys.stdin.readline())
        print("Tools list response:", response)
        
        # Send launch browser request
        launch_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "launch_browser",
            "params": {}
        }
        
        print(json.dumps(launch_request), flush=True)
        
        # Read response
        response = json.loads(sys.stdin.readline())
        print("Launch browser response:", response)
        
        # Keep reading until EOF
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            print("Additional response:", json.loads(line))
            
    except KeyboardInterrupt:
        print("Test interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    with handle_sigint():
        asyncio.run(test_extension())