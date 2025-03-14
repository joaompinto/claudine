"""
Tool interceptor functionality for Claude.
"""
from typing import Dict, Any, Callable, Optional

# Type definitions for interceptors
PreInterceptorType = Callable[[str, Dict[str, Any]], None]
PostInterceptorType = Callable[[str, Dict[str, Any], Any], Any]

def create_logging_interceptors(log_prefix: str = "Tool"):
    """
    Create simple logging interceptors for tool execution.
    
    Args:
        log_prefix: Prefix for log messages
        
    Returns:
        Tuple of (pre_interceptor, post_interceptor)
    """
    def pre_interceptor(tool_name: str, tool_input: Dict[str, Any]) -> None:
        """Log before tool execution."""
        print(f"{log_prefix} Executing: {tool_name}")
        print(f"{log_prefix} Input: {tool_input}")
    
    def post_interceptor(tool_name: str, tool_input: Dict[str, Any], result: Any) -> Any:
        """Log after tool execution."""
        print(f"{log_prefix} Result: {result}")
        return result
    
    return pre_interceptor, post_interceptor
