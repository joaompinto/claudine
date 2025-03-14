#!/usr/bin/env python3
from claudine import Agent
import sys

def main():
    """
    Example that demonstrates how to use the built-in token tracking and cost functionality.
    """
    # Initialize Agent
    agent = Agent(max_tokens=1000)
    
    # First prompt
    first_prompt = "Write a short poem about programming."
    first_response = agent.process_prompt(first_prompt)
    
    print(f"User: {first_prompt}")
    print(f"Claude: {first_response}")
    
    # Get token usage for the first message
    token_info = agent.get_token_usage()
    
    print("\nToken Usage Information:")
    print(f"Input tokens: {token_info.text_usage.input_tokens}")
    print(f"Output tokens: {token_info.text_usage.output_tokens}")
    print(f"Total tokens: {token_info.text_usage.total_tokens}")
    
    # Get cost information
    cost_info = agent.get_cost()
    
    print("\nCost Information:")
    print(f"Input cost: ${cost_info['text_cost'].input_cost:.6f} {cost_info['text_cost'].unit}")
    print(f"Output cost: ${cost_info['text_cost'].output_cost:.6f} {cost_info['text_cost'].unit}")
    print(f"Total cost: ${cost_info['total_cost'].total_cost:.6f} {cost_info['total_cost'].unit}")
    
    # Second prompt
    second_prompt = "Explain how token counting works in large language models."
    second_response = agent.process_prompt(second_prompt)
    
    print(f"\nUser: {second_prompt}")
    print(f"Claude: {second_response}")
    
    # Get updated token usage
    token_info = agent.get_token_usage()
    
    print("\nUpdated Token Usage:")
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
