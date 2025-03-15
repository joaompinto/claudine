"""
Tool management functionality for Claude.
Provides a system for registering, managing, and executing tools with Claude,
including schema generation, interceptors, and execution handling.
"""
from typing import Dict, List, Optional, Callable, Any, Tuple, Union
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
        self.text_editor_tool = None
    
    def register_tools(self, tools: List[Callable]):
        """
        Register multiple tools.
        
        Args:
            tools: List of functions to register as tools
        """
        for tool in tools:
            # Get tool name (use function name if not provided)
            tool_name = tool.__name__
            
            # Store the function
            self.tools[tool_name] = tool
            
            # Check if this is a text editor tool
            if tool_name == "str_replace_editor":
                self.text_editor_tool = tool
    
    def set_tool_interceptors(self, pre_interceptor: Optional[Callable] = None, 
                             post_interceptor: Optional[Callable] = None):
        """
        Set interceptors for tool execution.
        
        Args:
            pre_interceptor: Function to call before tool execution.
                             Must have signature (tool_name: str, tool_input: Dict[str, Any]) -> None
            post_interceptor: Function to call after tool execution.
                              Must have signature (tool_name: str, tool_input: Dict[str, Any], result: Any) -> Any
                              
        Raises:
            ValueError: If the interceptors don't have the correct signature
        """
        # Check pre_interceptor signature if provided
        if pre_interceptor:
            import inspect
            sig = inspect.signature(pre_interceptor)
            params = list(sig.parameters.keys())
            if len(params) != 2:
                raise ValueError(f"Pre-interceptor must have exactly 2 parameters: (tool_name, tool_input). Got {len(params)} parameters: {params}")
        
        # Check post_interceptor signature if provided
        if post_interceptor:
            import inspect
            sig = inspect.signature(post_interceptor)
            params = list(sig.parameters.keys())
            if len(params) != 3:
                raise ValueError(f"Post-interceptor must have exactly 3 parameters: (tool_name, tool_input, result). Got {len(params)} parameters: {params}")
        
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
            # Special handling for text editor tool
            if name == "str_replace_editor" and self.text_editor_tool:
                # For text editor, only include name and type
                schemas.append({
                    "name": "str_replace_editor",
                    "type": "text_editor_20250124"
                })
            else:
                schema = generate_tool_schema(func, name)
                schemas.append(schema)
        
        return schemas
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Union[str, Tuple[str, bool]]:
        """
        Execute a tool with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result as a string or a tuple of (content, is_error)
        """
        # Check if this is a text editor tool request
        if tool_name == "str_replace_editor" and self.text_editor_tool:
            tool_func = self.text_editor_tool
        else:
            # Get the tool function
            tool_func = self.tools.get(tool_name)
        
        if not tool_func:
            return (f"Error: Tool '{tool_name}' not found", True)
        
        # Call pre-interceptor if available
        if self.pre_interceptor:
            self.pre_interceptor(tool_name, tool_input)
        
        # Execute the tool
        result = tool_func(**tool_input)
        
        # Call post-interceptor if available
        if self.post_interceptor:
            result = self.post_interceptor(tool_name, tool_input, result)
        
        # Handle tuple case for error reporting
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], bool):
            content, is_error = result
            # Convert content to string if it's not already
            if not isinstance(content, str):
                if isinstance(content, (dict, list)):
                    content = json.dumps(content)
                else:
                    content = str(content)
            return (content, is_error)
        
        # Convert result to string if it's not already
        if not isinstance(result, str):
            if isinstance(result, (dict, list)):
                result = json.dumps(result)
            else:
                result = str(result)
        
        return result