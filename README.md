# Claudine

A Python wrapper for the Anthropic Claude API that simplifies tool use, token tracking, and agent functionality.

## Installation

```bash
# Using uv
uv pip install -e .

# With development dependencies
uv pip install -e ".[dev]"
```

## Features

- Easy integration with Claude 3 models
- Tool registration and management
- Token usage tracking and reporting
- Cost information tracking
- Support for tool interceptors
- Simplified message handling

## Quick Start

```python
from claudine import Agent

# Initialize the agent
agent = Agent()

# Process a prompt
response = agent.process_prompt("Write a short poem about programming.")
print(response)

# Get token usage information
token_info = agent.get_token_usage()
print(f"Total tokens used: {token_info.total_usage.total_tokens}")

# Get cost information
cost_info = agent.get_cost()
print(f"Total cost: ${cost_info['total_cost'].total_cost:.6f} {cost_info['total_cost'].unit}")
```

## Tool Usage

```python
from claudine import Agent

def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation here
    return f"Results for: {query}"

# Initialize agent with tools
agent = Agent(
    tools=[search_web]
)

# Process a prompt that might use tools
response = agent.process_prompt("What's the weather in London?")
print(response)
```

## Text Editor Tool

Claudine supports Claude's text editor tool for code editing and file manipulation:

```python
from claudine import Agent

def handle_editor_tool(**kwargs):
    """Handle text editor tool requests from Claude."""
    cmd_name = kwargs.get("command")
    
    # Handle different commands (view, edit, etc.)
    if cmd_name == "view":
        path = kwargs.get("path")
        # Implement file viewing logic
        return "File content here"
    elif cmd_name == "edit":
        # Implement file editing logic
        return "File edited successfully"
    
    return str(kwargs)

# Initialize agent with text editor tool
agent = Agent(
    text_editor=handle_editor_tool
)

# Process a prompt that might use the text editor
response = agent.process_prompt("Fix the bug in file.py")
print(response)
```

The text editor tool supports various commands like `view`, `edit`, and others that Claude may use to interact with your codebase.

## Token Tracking

Claudine provides detailed token usage information:

```python
token_info = agent.get_token_usage()

# Text usage
print(f"Text input tokens: {token_info.text_usage.input_tokens}")
print(f"Text output tokens: {token_info.text_usage.output_tokens}")

# Tool usage
print(f"Tool input tokens: {token_info.tools_usage.input_tokens}")
print(f"Tool output tokens: {token_info.tools_usage.output_tokens}")

# Total usage
print(f"Total tokens: {token_info.total_usage.total_tokens}")
```

## Cost Tracking

Claudine also provides detailed cost information:

```python
cost_info = agent.get_cost()

# Text costs
print(f"Text input cost: ${cost_info['text_cost'].input_cost:.6f} {cost_info['text_cost'].unit}")
print(f"Text output cost: ${cost_info['text_cost'].output_cost:.6f} {cost_info['text_cost'].unit}")
print(f"Text total cost: ${cost_info['text_cost'].total_cost:.6f} {cost_info['text_cost'].unit}")

# Tool costs
print(f"Tool input cost: ${cost_info['tools_cost'].input_cost:.6f} {cost_info['tools_cost'].unit}")
print(f"Tool output cost: ${cost_info['tools_cost'].output_cost:.6f} {cost_info['tools_cost'].unit}")
print(f"Tool total cost: ${cost_info['tools_cost'].total_cost:.6f} {cost_info['tools_cost'].unit}")

# Total cost
print(f"Total cost: ${cost_info['total_cost'].total_cost:.6f} {cost_info['total_cost'].unit}")

# Cost by tool
for tool_name, cost in cost_info['by_tool'].items():
    print(f"Tool: {tool_name}")
    print(f"  Input cost: ${cost.input_cost:.6f} {cost.unit}")
    print(f"  Output cost: ${cost.output_cost:.6f} {cost.unit}")
    print(f"  Total cost: ${cost.total_cost:.6f} {cost.unit}")
```

## License

MIT
