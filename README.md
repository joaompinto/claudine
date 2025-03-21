# 🤖 Claudine

A Python wrapper for the Anthropic Claude API that simplifies tool use, token tracking, and agent functionality.

## 📦 Installation

```bash
# Using pip
pip install claudine
```

## ✨ Features

- 🔌 Easy integration with Claude API
- 🛠️ Tool registration and management
- 🔢 Token usage tracking and reporting
- 💰 Cost information tracking
- 📞 Support for tool callbacks
- 💬 Simplified message handling
- 🖥️ Built-in support for bash tool
- 🔄 Cache support for efficient token usage
- ⚙️ Flexible configuration parameters

## 🚀 Quick Start

```python
from claudine import Agent

# Initialize the agent with configuration parameters
agent = Agent(system_prompt="You are a helpful assistant that can answer questions.")

# Query Claude with a prompt
response = agent.query("Write a short poem about programming.")
print(response)

# Get token usage information
token_info = agent.get_tokens()
print(f"Total tokens used: {token_info.total_usage.total_tokens}")

# Get cost information
cost_info = agent.get_token_cost()
print(f"Total cost: {cost_info.format_total_cost()} {cost_info.unit}")
```

## 🔧 Tool Usage

```python
from claudine import Agent

def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation here
    return f"Results for: {query}"

# Initialize agent with tools
agent = Agent(
    tools=[search_web],
    instructions="You are a helpful assistant that can search the web for information."
)

# Query Claude with a prompt that might use tools
response = agent.query("What's the weather in London?")
print(response)
```

## 📝 Text Editor Tool

Claudine supports the text editor tool for Claude, allowing it to view and edit text files. You can implement your own text editor tool handler and pass it to the Agent:

```python
def handle_editor_tool(command, **kwargs):
    # Implement the text editor tool
    # ...

# Initialize the agent with the text editor tool
agent = Agent(text_editor_tool=handle_editor_tool)
```

The text editor tool supports the following commands:
- 👁️ `view`: View the contents of a file
- 🔄 `str_replace`: Replace text in a file
- ✨ `create`: Create a new file
- ➕ `insert`: Insert text at a specific position
- ↩️ `undo_edit`: Undo the last edit

For more information, see the [Anthropic documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/text-editor-tool).

Note: The built-in text_editor_wrapper has been removed in favor of allowing users to implement their own text editor tool handlers.

## 🖥️ Bash Tool

Claudine now supports the bash tool for Claude, allowing it to execute shell commands:

```python
def handle_bash_tool(command, restart=False):
    # Implement the bash tool
    # Return a tuple of (output, is_error)
    return f"Executed: {command}", False

# Initialize the agent with the bash tool
agent = Agent(bash_tool=handle_bash_tool)
```

Example usage:

```python
# Create an agent with a bash tool implementation
agent = Agent(
    bash_tool=my_bash_implementation,
    system_prompt="You are a helpful assistant that can execute bash commands."
)

# Ask the agent to perform a task using bash
response = agent.query("List the files in the current directory")
```

## 🔢 Token Tracking

Claudine provides detailed token usage information:

```python
token_info = agent.get_tokens()

# Text usage
print(f"Text input tokens: {token_info.text_usage.input_tokens}")
print(f"Text output tokens: {token_info.text_usage.output_tokens}")
print(f"Text cache creation tokens: {token_info.text_usage.cache_creation_input_tokens}")
print(f"Text cache read tokens: {token_info.text_usage.cache_read_input_tokens}")

# Tool usage
print(f"Tool input tokens: {token_info.tools_usage.input_tokens}")
print(f"Tool output tokens: {token_info.tools_usage.output_tokens}")
print(f"Tool cache creation tokens: {token_info.tools_usage.cache_creation_input_tokens}")
print(f"Tool cache read tokens: {token_info.tools_usage.cache_read_input_tokens}")

# Total usage
print(f"Total input tokens: {token_info.total_usage.input_tokens}")
print(f"Total output tokens: {token_info.total_usage.output_tokens}")
print(f"Total tokens: {token_info.total_usage.total_tokens}")
```

## 🧠 Cache Support

Claudine supports Claude's cache functionality, which can significantly reduce token costs for repeated or similar prompts:

```python
# Initialize agent
agent = Agent()

# First call will create a cache
response1 = agent.query("What is the capital of France?")

# Second call with the same prompt will use the cache
# Note: Caching is only performed when the input is >1024 tokens
response2 = agent.query("What is the capital of France?")

# Get token usage with cache information
token_info = agent.get_tokens()
print(f"Cache creation tokens: {token_info.total_usage.cache_creation_input_tokens}")
print(f"Cache read tokens: {token_info.total_usage.cache_read_input_tokens}")

# Get cost information including cache costs
cost_info = agent.get_token_cost()
print(f"Cache creation cost: ${cost_info.cache_creation_cost:.6f} {cost_info.unit}")
print(f"Cache read cost: ${cost_info.cache_read_cost:.6f} {cost_info.unit}")
print(f"Cache savings: ${cost_info.cache_delta:.6f} {cost_info.unit}")
```

Cache usage is automatically tracked and reflected in token usage and cost calculations. Using the cache can result in significant cost savings for repeated queries:

- Cache creation costs 25% more than standard input tokens
- Cache reads cost only 10% of the standard input token price
- The `cache_delta` field shows your savings from using the cache

The API for accessing token and cost information has been improved with direct attribute access instead of dictionary access.

## 🐛 Debugging

Claudine provides a verbose mode to help you understand what's happening behind the scenes:

```python
# Initialize agent with verbose mode
agent = Agent(verbose=True)

# Query Claude with a prompt
response = agent.query("Hello, Claude!")
```

When verbose mode is enabled, Claudine will print detailed information about the API requests being sent to Claude, including:
- 💬 Message content
- 🛠️ Tool definitions
- ⚙️ Model parameters
- 🔢 Token usage and cache metrics

This is particularly useful when debugging tool use, cache behavior, and tool interactions. The previous `debug_mode` parameter has been renamed to `verbose` for clarity.

## ⚙️ Configuration Parameters

Claudine allows you to configure Claude's behavior using the `config_params` dictionary:

```python
# Initialize agent with configuration parameters
agent = Agent(
    config_params={
        "top_p": 0.9,
        "top_k": 50
    }
)
```

The `config_params` dictionary accepts any valid Claude API parameters such as:
- `top_p`: Controls diversity via nucleus sampling
- `top_k`: Controls diversity via limiting the token pool
- Other model parameters as supported by the Claude API

For more information on available parameters, see the [Anthropic API documentation](https://docs.anthropic.com/claude/reference/messages-create).

## 💬 Message History Management

Claudine provides methods to manage conversation history:

```python
# Get the current conversation messages
messages = agent.get_messages()

# Get only the text messages (filtering out tool-related messages)
text_messages = agent.get_messages(filter_out_tools=True)

# Set a specific conversation history
agent.set_messages(my_messages)

# Reset the conversation
agent.reset()
```

## 💰 Cost Tracking

Claudine provides detailed cost information, including cache-related costs. The API has been updated to use direct attribute access instead of dictionary access:

```python
cost_info = agent.get_token_cost()

# Text costs
print(f"Text input cost: ${cost_info.text_cost.input_cost:.6f} {cost_info.text_cost.unit}")
print(f"Text output cost: ${cost_info.text_cost.output_cost:.6f} {cost_info.text_cost.unit}")
print(f"Text total cost: ${cost_info.text_cost.total_cost:.6f} {cost_info.text_cost.unit}")

# Tool costs
print(f"Tool input cost: ${cost_info.tools_cost.input_cost:.6f} {cost_info.tools_cost.unit}")
print(f"Tool output cost: ${cost_info.tools_cost.output_cost:.6f} {cost_info.tools_cost.unit}")
print(f"Tool total cost: ${cost_info.tools_cost.total_cost:.6f} {cost_info.tools_cost.unit}")

# Cache costs
print(f"Cache creation cost: ${cost_info.total_cost.cache_creation_cost:.6f} {cost_info.total_cost.unit}")
print(f"Cache read cost: ${cost_info.total_cost.cache_read_cost:.6f} {cost_info.total_cost.unit}")

# Total cost
print(f"Total cost: ${cost_info.total_cost.total_cost:.6f} {cost_info.total_cost.unit}")

# Cost by tool
for tool_name, cost in cost_info.by_tool.items():
    print(f"Tool: {tool_name}")
    print(f"  Input cost: ${cost.input_cost:.6f} {cost.unit}")
    print(f"  Output cost: ${cost.output_cost:.6f} {cost.unit}")
    print(f"  Total cost: ${cost.total_cost:.6f} {cost.unit}")
```

The cost tracking is based on the current Claude API pricing model (as of 2025):
- Input tokens: $3.00 per million tokens
- Output tokens: $15.00 per million tokens
- Cache creation: 125% of the base input token price
- Cache read: 10% of the base input token price

This pricing structure allows for significant cost savings when using Claude's cache functionality for repeated or similar queries.

## 📄 License

MIT
