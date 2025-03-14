"""
Tool management functionality for Claude.
"""
from typing import Dict, List, Optional, Callable, Any, Tuple
import inspect
import json
from .schema import generate_tool_schema

class ToolManager:
    """
    Manages tool registration, schema generation, and execution.
    """
    
    def __init__(self):
        """Initialize an empty tool manager."""
        self.tools = {}
        self.pre_interceptor = None
        self.post_interceptor = None
    
    def register_tool(self, func: Callable, name: Optional[str] = None, 
                     description: Optional[str] = None) -> str:
        """
        Register a function as a tool.
        
        Args:
            func: Function to register as a tool
            name: Optional name for the tool (defaults to function name)
            description: Optional description for the tool
            
        Returns:
            Name of the registered tool
        """
        # Get tool name (use function name if not provided)
        tool_name = name if name else func.__name__
        
        # Store the function
        self.tools[tool_name] = func
        
        # Return the tool name
        return tool_name
    
    def register_tools(self, tools: List[Callable]):
        """
        Register multiple tools.
        
        Args:
            tools: List of functions to register as tools
        """
        for tool in tools:
            self.register_tool(tool)
    
    def set_tool_interceptors(self, pre_interceptor: Optional[Callable] = None, 
                             post_interceptor: Optional[Callable] = None):
        """
        Set interceptors for tool execution.
        
        Args:
            pre_interceptor: Function to call before tool execution
            post_interceptor: Function to call after tool execution
        """
        self.pre_interceptor = pre_interceptor
        self.post_interceptor = post_interceptor
    
    def get_tool_schemas(self) -> List[Dict]:
        """
        Get JSON schemas for all registered tools.
        
        Returns:
            List of tool schemas
        """
        schemas = []
        
        for name, func in self.tools.items():
            schema = generate_tool_schema(func, name)
            schemas.append(schema)
        
        return schemas
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result as a string
        """
        # Get the tool function
        tool_func = self.tools.get(tool_name)
        
        if not tool_func:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            # Call pre-interceptor if available
            if self.pre_interceptor:
                self.pre_interceptor(tool_name, tool_input)
            
            # Execute the tool
            result = tool_func(**tool_input)
            
            # Call post-interceptor if available
            if self.post_interceptor:
                result = self.post_interceptor(tool_name, tool_input, result)
            
            # Convert result to string if it's not already
            if not isinstance(result, str):
                if isinstance(result, (dict, list)):
                    result = json.dumps(result)
                else:
                    result = str(result)
            
            return result
        
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
