"""Integration tests for AnthropicProvider."""

import os
from aiagent.providers.anthropic import AnthropicProvider

def test_send_message_integration():
    """Integration test: Actually sends a message to Anthropic API."""
    # Get real API key from environment
    api_key = os.environ.get("MY_ANTHROPIC_API_KEY")
    
    # Use the cheapest model to minimize costs
    provider = AnthropicProvider(api_key=api_key, model="claude-3-haiku-20240307")
    
    # Send a simple test message with minimal tokens
    test_message = "Reply with just 'Test successful' and nothing else."
    response = provider.send_message(test_message, max_tokens=20)
    
    # Verify we got a response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Optional: Check if response contains expected text (may vary)
    print(f"Actual API response: {response}")
