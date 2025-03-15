"""
Example demonstrating the callback signature validation.
"""
from claudine import Agent, create_logging_callbacks

def main():
    # These callbacks have the correct signature
    pre_callback, post_callback = create_logging_callbacks()
    
    # This will work fine
    agent = Agent(
        tool_callbacks=(pre_callback, post_callback)
    )
    print("Successfully set up agent with valid callbacks")
    
    # Invalid pre-callback (wrong number of parameters)
    def invalid_pre_callback(tool_name):
        print(f"Invalid pre-callback called for: {tool_name}")
    
    try:
        agent = Agent(
            tool_callbacks=(invalid_pre_callback, post_callback)
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Invalid post-callback (wrong number of parameters)
    def invalid_post_callback(tool_name, tool_input):
        print(f"Invalid post-callback called for: {tool_name}")
        return "Modified result"
    
    try:
        agent = Agent(
            tool_callbacks=(pre_callback, invalid_post_callback)
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    print("All tests completed")

if __name__ == "__main__":
    main()
