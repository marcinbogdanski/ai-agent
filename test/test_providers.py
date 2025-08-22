"""Integration tests for AnthropicProvider."""

import os
from aiagent.providers.anthropic import AnthropicProvider

def test_send_text_message_integration():
    """Integration test: Tests the send_text_message convenience method."""
    # Get real API key from environment
    api_key = os.environ.get("MY_ANTHROPIC_API_KEY")
    
    # Use the cheapest model to minimize costs
    provider = AnthropicProvider(api_key=api_key, model="claude-3-haiku-20240307")
    
    # Send a simple test message with minimal tokens
    test_message = "Reply with just 'Test successful' and nothing else."
    response = provider.send_text_message(test_message, max_tokens=20)
    
    # Verify we got a response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Optional: Check if response contains expected text (may vary)
    print(f"Actual API response: {response}")

def test_send_message_integration():
    """Integration test: Tests the send_message method with full conversation."""
    # Get real API key from environment
    api_key = os.environ.get("MY_ANTHROPIC_API_KEY")
    
    # Use the cheapest model to minimize costs
    provider = AnthropicProvider(api_key=api_key, model="claude-3-haiku-20240307")
    
    # Send a conversation with minimal tokens
    messages = [
        {"role": "user", "content": "Reply with just 'Test successful' and nothing else."}
    ]
    response = provider.send_message(messages, max_tokens=20)
    
    # Verify we got a response object
    assert response is not None
    assert 'content' in response
    assert isinstance(response['content'], str)
    assert len(response['content']) > 0

    # Extract and verify text
    response_text = response['content']
    assert isinstance(response_text, str)
    assert len(response_text) > 0
    
    print(f"Actual API response text: {response_text}")
