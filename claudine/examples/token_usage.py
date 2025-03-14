#!/usr/bin/env python3
from claudine import Agent
import sys

def main():
    """
    Example that demonstrates how to obtain token usage and cost information
    after making calls to the Claudine Agent.
    """
    
    # Initialize Agent
    agent = Agent(max_tokens=1000, temperature=0.7)
    
    # Simple message to the API
    response = agent.process_prompt("Write a short poem about programming.")
    
    # Print the response
    print("Claude's response:")
    print(response)
    print("\n" + "-" * 50 + "\n")
    
    # Get token usage information
    token_info = agent.get_token_usage()
    
    print("Token Usage Information:")
    print(f"Text input tokens: {token_info.text_usage.input_tokens}")
    print(f"Text output tokens: {token_info.text_usage.output_tokens}")
    print(f"Text total tokens: {token_info.text_usage.total_tokens}")
    print(f"Tool input tokens: {token_info.tools_usage.input_tokens}")
    print(f"Tool output tokens: {token_info.tools_usage.output_tokens}")
    print(f"Tool total tokens: {token_info.tools_usage.total_tokens}")
    print(f"Total input tokens: {token_info.total_usage.input_tokens}")
    print(f"Total output tokens: {token_info.total_usage.output_tokens}")
    print(f"Total tokens: {token_info.total_usage.total_tokens}")
    
    # Get cost information
    cost_info = agent.get_cost()
    
    print("\nCost Information:")
    print(f"Text input cost: ${cost_info['text_cost'].input_cost:.6f} {cost_info['text_cost'].unit}")
    print(f"Text output cost: ${cost_info['text_cost'].output_cost:.6f} {cost_info['text_cost'].unit}")
    print(f"Text total cost: ${cost_info['text_cost'].total_cost:.6f} {cost_info['text_cost'].unit}")
    print(f"Tool input cost: ${cost_info['tools_cost'].input_cost:.6f} {cost_info['tools_cost'].unit}")
    print(f"Tool output cost: ${cost_info['tools_cost'].output_cost:.6f} {cost_info['tools_cost'].unit}")
    print(f"Tool total cost: ${cost_info['tools_cost'].total_cost:.6f} {cost_info['tools_cost'].unit}")
    print(f"Total cost: ${cost_info['total_cost'].total_cost:.6f} {cost_info['total_cost'].unit}")
    
    # Example with a longer prompt
    print("\n" + "-" * 50 + "\n")
    print("Example with a longer prompt:")
    
    longer_response = agent.process_prompt("Explain how token counting works in large language models and why it matters for API usage.")
    
    # Print the response
    print("Claude's response:")
    print(longer_response)
    print("\n" + "-" * 50 + "\n")
    
    # Get updated token usage information
    token_info = agent.get_token_usage()
    
    print("Updated Token Usage Information:")
    print(f"Total input tokens: {token_info.total_usage.input_tokens}")
    print(f"Total output tokens: {token_info.total_usage.output_tokens}")
    print(f"Total tokens: {token_info.total_usage.total_tokens}")
    
    # Get updated cost information
    cost_info = agent.get_cost()
    
    print("\nUpdated Cost Information:")
    print(f"Total cost: ${cost_info['total_cost'].total_cost:.6f} {cost_info['total_cost'].unit}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
