"""
Common utility functions for Claudine.
"""
from typing import Dict, List, Optional, Any
import uuid
import json

def generate_message_id() -> str:
    """
    Generate a unique message ID.
    
    Returns:
        Unique message ID
    """
    return f"msg_{uuid.uuid4().hex[:24]}"

def extract_text_content(content_blocks: List[Any]) -> str:
    """
    Extract text content from content blocks.
    
    Args:
        content_blocks: List of content blocks from Claude's response
        
    Returns:
        Concatenated text content
    """
    text_content = ""
    
    for block in content_blocks:
        if hasattr(block, 'type') and block.type == "text":
            text_content += block.text
    
    return text_content

def format_tool_result(tool_use_id: str, result: str) -> Dict:
    """
    Format a tool result for sending to Claude.
    
    Args:
        tool_use_id: ID of the tool use
        result: Result of the tool execution
        
    Returns:
        Formatted tool result
    """
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": result
    }
