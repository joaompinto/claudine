"""
Example demonstrating the interceptor signature validation.
"""
from claudine import Agent, create_logging_interceptors

def main():
    # These interceptors have the correct signature
    pre_interceptor, post_interceptor = create_logging_interceptors()
    
    # This will work fine
    agent = Agent(
        tool_interceptors=(pre_interceptor, post_interceptor)
    )
    print("Successfully set up agent with valid interceptors")
    
    # Invalid pre-interceptor (wrong number of parameters)
    def invalid_pre_interceptor(tool_name):
        print(f"Invalid pre-interceptor called for: {tool_name}")
    
    try:
        agent = Agent(
            tool_interceptors=(invalid_pre_interceptor, post_interceptor)
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Invalid post-interceptor (wrong number of parameters)
    def invalid_post_interceptor(tool_name, tool_input):
        print(f"Invalid post-interceptor called for: {tool_name}")
        return "Modified result"
    
    try:
        agent = Agent(
            tool_interceptors=(pre_interceptor, invalid_post_interceptor)
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    print("All tests completed")

if __name__ == "__main__":
    main()
