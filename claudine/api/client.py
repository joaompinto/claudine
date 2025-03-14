"""
API client wrapper for Anthropic's Claude API.
"""
from typing import Dict, List, Optional, Any
import anthropic

class ApiClient:
    """
    Wrapper for the Anthropic API client.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: Anthropic API key. If None, will try to get from environment variable.
        """
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def create_message(self, 
                      model: str,
                      messages: List[Dict[str, Any]],
                      max_tokens: int = 1024,
                      temperature: float = 0.7,
                      system: Optional[str] = None,
                      tools: Optional[List[Dict]] = None,
                      tool_choice: Optional[Dict] = None) -> anthropic.types.Message:
        """
        Create a message using the Anthropic API.
        
        Args:
            model: Claude model to use
            messages: List of messages in the conversation
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            system: System prompt to guide the model's behavior
            tools: List of tool schemas
            tool_choice: Tool choice configuration
            
        Returns:
            Anthropic API response
        """
        # Prepare API call parameters
        api_params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        # Add system prompt if provided
        if system:
            api_params["system"] = system
        
        # Add tools if provided
        if tools:
            api_params["tools"] = tools
            
            # Add tool_choice if provided
            if tool_choice:
                api_params["tool_choice"] = tool_choice
        
        # Make the API call
        return self.client.messages.create(**api_params)
