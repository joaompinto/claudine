from typing import Dict, List, Optional, Union
from .api.models import TokenUsage, TokenUsageInfo, ModelPricing, TokenPricing

# Default model to use for pricing
DEFAULT_MODEL = "claude-3-7-sonnet-20250219"

# Model pricing data
MODEL_PRICING = {
    DEFAULT_MODEL: ModelPricing(
        input_tokens=TokenPricing(
            cost_per_million_tokens=3.0,
            unit="USD"
        ),
        output_tokens=TokenPricing(
            cost_per_million_tokens=15.0,
            unit="USD"
        )
    )
}

class TokenTracker:
    """
    Tracks token usage for Claude API calls.
    """
    
    def __init__(self):
        """Initialize an empty token tracker."""
        self.messages = {}  # Dictionary to store message token usage by message ID
    
    def add_message(self, message_id: str, input_tokens: int, output_tokens: int, 
                   is_tool_related: bool = False, tool_name: Optional[str] = None,
                   parent_message_id: Optional[str] = None):
        """
        Add a message's token usage to the tracker.
        
        Args:
            message_id: Unique ID of the message
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            is_tool_related: Whether this message is part of a tool call sequence
            tool_name: Name of the tool if is_tool_related is True
            parent_message_id: ID of the parent message that initiated the tool call
        """
        self.messages[message_id] = {
            "message_id": message_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "is_tool_related": is_tool_related,
            "tool_name": tool_name,
            "parent_message_id": parent_message_id
        }
    
    def get_token_usage(self, message_id: Optional[str] = None) -> Union[Dict, TokenUsageInfo]:
        """
        Get token usage information for a specific message or consolidated usage.
        
        Args:
            message_id: Optional ID of the message to get token usage for.
                        If None, returns consolidated token usage information.
        
        Returns:
            If message_id is provided: Token usage information for that message
            If message_id is None: TokenUsageInfo with text and tool usage information
        """
        if message_id:
            return self.messages.get(message_id, {})
        
        # Calculate total usage
        total_input = sum(msg["input_tokens"] for msg in self.messages.values())
        total_output = sum(msg["output_tokens"] for msg in self.messages.values())
        
        # Calculate tool-related usage
        tool_messages = [msg for msg in self.messages.values() if msg["is_tool_related"]]
        tool_input = sum(msg["input_tokens"] for msg in tool_messages)
        tool_output = sum(msg["output_tokens"] for msg in tool_messages)
        
        # Calculate text-only usage
        text_input = total_input - tool_input
        text_output = total_output - tool_output
        
        # Create TokenUsage objects
        text_usage = TokenUsage(
            input_tokens=text_input,
            output_tokens=text_output
        )
        
        tools_usage = TokenUsage(
            input_tokens=tool_input,
            output_tokens=tool_output
        )
        
        # Calculate usage by tool
        by_tool = {}
        for msg in self.messages.values():
            if msg["is_tool_related"] and msg["tool_name"]:
                tool_name = msg["tool_name"]
                
                if tool_name not in by_tool:
                    by_tool[tool_name] = {
                        "input_tokens": 0,
                        "output_tokens": 0
                    }
                
                by_tool[tool_name]["input_tokens"] += msg["input_tokens"]
                by_tool[tool_name]["output_tokens"] += msg["output_tokens"]
        
        # Convert by_tool to use TokenUsage objects
        by_tool_usage = {}
        for tool_name, usage in by_tool.items():
            by_tool_usage[tool_name] = TokenUsage(
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"]
            )
        
        return TokenUsageInfo(
            text_usage=text_usage,
            tools_usage=tools_usage,
            by_tool=by_tool_usage
        )
    
    def get_cost(self, message_id: Optional[str] = None) -> Dict:
        """
        Get cost information for token usage.
        
        Args:
            message_id: Optional ID of the message to get cost for.
                        If None, returns consolidated cost information.
        
        Returns:
            Dictionary with cost information
        """
        # Get token usage
        usage = self.get_token_usage(message_id)
        
        # Get pricing for the default model
        pricing = MODEL_PRICING.get(DEFAULT_MODEL)
        if not pricing:
            return {"error": f"No pricing information available for model {DEFAULT_MODEL}"}
        
        # If it's a single message, calculate cost for that message
        if isinstance(usage, dict):
            input_cost = pricing.input_tokens.calculate_cost(usage.get("input_tokens", 0))
            output_cost = pricing.output_tokens.calculate_cost(usage.get("output_tokens", 0))
            total_cost = input_cost + output_cost
            
            return {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "unit": pricing.input_tokens.unit
            }
        
        # Calculate cost for consolidated usage
        return usage.calculate_cost(pricing)
    
    def reset(self):
        """Reset all token usage data."""
        self.messages = {}
