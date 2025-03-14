import inspect
from typing import Any, Callable, Dict, List, Optional, Union, get_type_hints

class ToolManager:
    """
    Manages tool registration, schema generation, and execution for the Agent.
    """
    
    def __init__(self):
        """Initialize an empty tool manager."""
        self.registered_tools = {}
        
        # Default interceptors
        self.pre_tool_interceptor = self._default_pre_tool_interceptor
        self.post_tool_interceptor = self._default_post_tool_interceptor
    
    def _default_pre_tool_interceptor(self, tool_name: str, tool_input: Dict[str, Any], 
                                    preamble_text: str = "") -> Dict[str, Any]:
        """
        Default interceptor called before a tool is executed.
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters for the tool
            preamble_text: Any text Claude generated before the tool call
            
        Returns:
            Possibly modified tool input
        """
        return tool_input
    
    def _default_post_tool_interceptor(self, tool_name: str, tool_input: Dict[str, Any], 
                                     result: Any, error: Optional[Exception] = None,
                                     preamble_text: str = "") -> Any:
        """
        Default interceptor called after a tool is executed.
        
        Args:
            tool_name: Name of the tool that was called
            tool_input: Input parameters that were passed to the tool
            result: Result returned by the tool (None if there was an error)
            error: Exception that occurred during execution (None if successful)
            preamble_text: Any text Claude generated before the tool call
            
        Returns:
            Possibly modified result
        """
        return result
    
    def set_tool_interceptors(self, pre_interceptor: Optional[Callable] = None, 
                            post_interceptor: Optional[Callable] = None):
        """
        Set custom interceptors for tool calls.
        
        Args:
            pre_interceptor: Function to call before executing a tool
            post_interceptor: Function to call after executing a tool
        """
        if pre_interceptor:
            self.pre_tool_interceptor = pre_interceptor
        if post_interceptor:
            self.post_tool_interceptor = post_interceptor
    
    def register_tool(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        """
        Register a function as a tool.
        
        Args:
            func: The function to register
            name: Optional custom name for the tool (defaults to function name)
            description: Optional description of what the tool does
            
        Returns:
            The original function
        """
        func_name = name or func.__name__
        func_description = description or func.__doc__ or f"Function {func_name}"
        
        # Extract clean description
        if func_description:
            func_description = func_description.split('\n\n')[0]
        
        # Build the schema based on function signature and type hints
        schema = self._build_schema_from_function(func)
        
        # Store the function and its schema
        self.registered_tools[func_name] = {
            "function": func,
            "schema": {
                "name": func_name,
                "description": func_description,
                "input_schema": schema
            }
        }
        
        return func
    
    def register_tools(self, tools: List[Callable]):
        """
        Register multiple tools at once.
        
        Args:
            tools: List of functions to register as tools
        """
        for tool in tools:
            self.register_tool(tool)
    
    def _build_schema_from_function(self, func: Callable) -> Dict:
        """
        Build a JSON schema based on the function's signature and type hints.
        
        Args:
            func: The function to analyze
            
        Returns:
            A JSON schema dictionary describing the function parameters
        """
        signature = inspect.signature(func)
        hints = get_type_hints(func)
        
        properties = {}
        required = []
        
        for param_name, param in signature.parameters.items():
            # Skip self parameter for methods
            if param_name == 'self':
                continue
                
            param_type = hints.get(param_name, Any)
            param_doc = self._extract_param_doc(func, param_name)
            
            # Handle various types
            if param_type == str:
                param_schema = {"type": "string"}
            elif param_type == int:
                param_schema = {"type": "integer"}
            elif param_type == float:
                param_schema = {"type": "number"}
            elif param_type == bool:
                param_schema = {"type": "boolean"}
            elif hasattr(param_type, '__origin__') and param_type.__origin__ is list:
                param_schema = {"type": "array"}
            elif hasattr(param_type, '__origin__') and param_type.__origin__ is dict:
                param_schema = {"type": "object"}
            else:
                # Default to string for complex types
                param_schema = {"type": "string"}
            
            # Add description if available
            if param_doc:
                param_schema["description"] = param_doc
                
            properties[param_name] = param_schema
            
            # Mark as required if it doesn't have a default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema["required"] = required
            
        return schema
    
    def _extract_param_doc(self, func: Callable, param_name: str) -> Optional[str]:
        """
        Extract parameter documentation from function docstring.
        
        Args:
            func: The function to analyze
            param_name: The parameter name to find documentation for
            
        Returns:
            Parameter description if found, None otherwise
        """
        if not func.__doc__:
            return None
            
        docstring = inspect.cleandoc(func.__doc__)
        
        # Try to find param in the docstring using common formats
        # Look for :param param_name: or Args: param_name:
        param_patterns = [
            f":param {param_name}:", 
            f"@param {param_name}:",
            f"Args:\n    {param_name}:",
            f"Arguments:\n    {param_name}:"
        ]
        
        for pattern in param_patterns:
            if pattern in docstring:
                parts = docstring.split(pattern, 1)[1].strip()
                desc = parts.split('\n', 1)[0].strip()
                return desc
                
        return None
    
    def get_tools_schemas(self) -> List[Dict]:
        """
        Get the schema definitions for all registered tools.
        
        Returns:
            List of tool schema definitions
        """
        return [tool_info["schema"] for tool_info in self.registered_tools.values()]
    
    def get_tools_names(self) -> List[str]:
        """
        Get the names of all registered tools.
        
        Returns:
            List of tool names
        """
        return list(self.registered_tools.keys())
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any], preamble_text: str = "") -> Any:
        """
        Execute a registered tool with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            preamble_text: Any text Claude generated before the tool call
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool is not registered
        """
        if tool_name not in self.registered_tools:
            raise ValueError(f"Tool '{tool_name}' is not registered")
            
        tool_info = self.registered_tools[tool_name]
        func = tool_info["function"]
        
        # Apply pre-execution interceptor
        modified_input = self.pre_tool_interceptor(tool_name, tool_input, preamble_text)
        
        # Execute the tool
        error = None
        result = None
        try:
            result = func(**modified_input)
        except Exception as e:
            error = e
            
        # Apply post-execution interceptor
        return self.post_tool_interceptor(tool_name, modified_input, result, error, preamble_text)
