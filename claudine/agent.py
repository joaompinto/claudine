"""
Main Agent class for Claudine.
"""
from typing import Dict, List, Optional, Callable, Any, Tuple, Union
import anthropic

from .api.client import ApiClient
from .api.models import ResponseType, ToolUseResponse, TextResponse, TokenUsage, TokenUsageInfo
from .tools.manager import ToolManager
from .token_tracking import TokenTracker, DEFAULT_MODEL
from .utils.helpers import generate_message_id, extract_text_content, format_tool_result

class Agent:
    """
    Agent for interacting with Claude.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                max_tokens: int = 1024, temperature: float = 0.7,
                max_rounds: int = 30, instructions: Optional[str] = None,
                tools: Optional[List[Callable]] = None,
                tool_interceptors: Optional[Tuple[Optional[Callable], Optional[Callable]]] = None,
                disable_parallel_tool_use: bool = True):
        """
        Initialize the Agent wrapper with your Anthropic API key, model parameters, and tools.
        If api_key is not provided, it will use the ANTHROPIC_API_KEY environment variable.
        
        Args:
            api_key: Anthropic API key
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            max_rounds: Maximum number of rounds for tool use
            instructions: Instructions to guide the model's behavior (used as system prompt)
            tools: List of functions to register as tools
            tool_interceptors: Tuple of (pre_interceptor, post_interceptor) callables for tool execution
            disable_parallel_tool_use: Disable parallel tool use to ensure accurate token accounting
        """
        # Initialize API client
        self.api_client = ApiClient(api_key=api_key)
        
        # Store parameters
        self.messages = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_rounds = max_rounds
        self.system = instructions
        
        # Initialize token tracker
        self.token_tracker = TokenTracker()
        
        # Initialize tool manager
        self.tool_manager = ToolManager()
        
        # Register tools if provided
        if tools:
            self.tool_manager.register_tools(tools)
        
        # Set tool interceptors if provided
        if tool_interceptors:
            pre_interceptor, post_interceptor = tool_interceptors
            self.tool_manager.set_tool_interceptors(pre_interceptor, post_interceptor)
        
        # Disable parallel tool use to ensure accurate token accounting
        self.disable_parallel_tool_use = disable_parallel_tool_use
    
    def set_tool_interceptors(self, pre_interceptor: Optional[Callable] = None, 
                            post_interceptor: Optional[Callable] = None):
        """
        Set interceptors for tool execution.
        
        Args:
            pre_interceptor: Function to call before tool execution
            post_interceptor: Function to call after tool execution
        """
        self.tool_manager.set_tool_interceptors(pre_interceptor, post_interceptor)
    
    def _call_claude(self, tools: List[Dict]) -> ResponseType:
        """
        Call Claude with the current messages and tools.
        
        Args:
            tools: List of tool schemas
            
        Returns:
            Claude's response as a ResponseType
        """
        # Set tool_choice with disable_parallel_tool_use parameter
        tool_choice = None
        if tools:
            tool_choice = {
                "type": "auto",
                "disable_parallel_tool_use": self.disable_parallel_tool_use
            }
        
        # Make the API call
        response = self.api_client.create_message(
            model=DEFAULT_MODEL,
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system,
            tools=tools,
            tool_choice=tool_choice
        )
        
        # Track token usage
        message_id = response.id
        
        # Check if this is a tool-related message
        is_tool_related = False
        tool_name = None
        parent_message_id = None
        
        # If this is a response to a tool result, it's tool-related
        if len(self.messages) >= 2 and isinstance(self.messages[-1].get("content"), list):
            for content_item in self.messages[-1].get("content", []):
                if isinstance(content_item, dict) and content_item.get("type") == "tool_result":
                    is_tool_related = True
                    # Try to find the parent message that initiated this tool call
                    if len(self.messages) >= 3:
                        for content_item in self.messages[-2].get("content", []):
                            if isinstance(content_item, dict) and content_item.get("type") == "tool_use":
                                tool_name = content_item.get("name")
                                # Find the original message that triggered this tool
                                for i in range(len(self.messages) - 3, -1, -1):
                                    if self.messages[i].get("role") == "assistant":
                                        parent_message_id = f"msg_{i}"  # Create a pseudo-ID
                                        break
        
        self.token_tracker.add_message(
            message_id=message_id,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            is_tool_related=is_tool_related,
            tool_name=tool_name,
            parent_message_id=parent_message_id
        )
        
        # Check if tool use is requested
        if response.stop_reason == "tool_use":
            # Extract text and tool use from response
            text_content = ""
            tool_use = None
            
            for content_block in response.content:
                if content_block.type == "text":
                    text_content += content_block.text
                elif content_block.type == "tool_use":
                    tool_use = content_block
            
            if tool_use:
                return ToolUseResponse(
                    type="tool_use",
                    name=tool_use.name,
                    input=tool_use.input,
                    id=tool_use.id,
                    message_id=message_id,
                    preamble=text_content
                )
        
        # Regular text response
        text_content = extract_text_content(response.content)
        
        return TextResponse(
            type="text",
            text=text_content,
            message_id=message_id
        )
    
    def process_prompt(self, prompt: str) -> str:
        """
        Process a prompt and return Claude's response.
        
        Args:
            prompt: User prompt
            
        Returns:
            Claude's response as a string
        """
        # Add user message to conversation
        self.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Get tool schemas
        tools = self.tool_manager.get_tool_schemas()
        
        # Call Claude
        response = self._call_claude(tools)
        
        # If tool use is requested, execute the tool
        rounds = 0
        while response.type == "tool_use" and rounds < self.max_rounds:
            # Add assistant message with tool use
            self.messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": response.id,
                        "name": response.name,
                        "input": response.input
                    }
                ]
            })
            
            # Execute the tool
            tool_result = self.tool_manager.execute_tool(response.name, response.input)
            
            # Add user message with tool result
            self.messages.append({
                "role": "user",
                "content": [
                    format_tool_result(response.id, tool_result)
                ]
            })
            
            # Call Claude again
            response = self._call_claude(tools)
            
            # Increment rounds
            rounds += 1
        
        # Add assistant message to conversation
        self.messages.append({
            "role": "assistant",
            "content": response.text
        })
        
        # Return the response text
        return response.text
    
    def get_token_usage(self) -> TokenUsageInfo:
        """
        Get token usage information.
        
        Returns:
            TokenUsageInfo object with usage details
        """
        return self.token_tracker.get_token_usage()
    
    def get_cost(self) -> Dict:
        """
        Get cost information for token usage.
        
        Returns:
            Dictionary with cost information
        """
        return self.token_tracker.get_cost()
    
    def set_model(self, model: str):
        """
        Set the model to use for the agent and update token tracker.
        
        Args:
            model: The model name
        """
        self.model = model
        self.token_tracker.set_model(model)
    
    def reset(self):
        """Reset the conversation history."""
        self.messages = []
        self.token_tracker.reset()
