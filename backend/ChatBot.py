import anthropic
import os
def call_claude_sonnet(prompt: str) -> str:
    """
    Calls the Claude 3.5 Sonnet API with the given prompt and returns the response.

    Args:
        prompt: The text prompt to send to the API.

    Returns:
        The text response from the Claude 3.5 Sonnet API, or an error message.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "Error: ANTHROPIC_API_KEY environment variable not set."

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,  # Adjust as needed
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        return response.content[0].text
    except anthropic.APIStatusError as e:
        return f"Anthropic API Status Error: {e}"
    except anthropic.APIConnectionError as e:
        return f"Anthropic API Connection Error: {e}"
    except anthropic.AuthenticationError as e:
        return f"Anthropic API Authentication Error: {e}"
    except anthropic.RateLimitError as e:
        return f"Anthropic API Rate Limit Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    
print(call_claude_sonnet("Hi"))
