"""Simple Anthropic LLM interface implementation."""

from typing import Any
import anthropic


class AnthropicProvider:
    """Minimal Anthropic LLM provider class."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-5-sonnet-20241022)
        """
        assert isinstance(api_key, str), "API key must be a string"
        assert isinstance(model, str), "Model must be a string"
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def send_message(self, messages: list[dict[str, str]], max_tokens: int) -> dict[str, str]:
        """Send messages to the LLM and get a response.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens in response (recommended: 32000)
            
        Returns:
            The full Anthropic Message response object
        """
        assert isinstance(messages, list), "Messages must be a list of dicts"
        assert isinstance(max_tokens, int), "max_tokens must be an integer"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )
       
        return {
            "role": "assistant",
            "content": response.content[0].text
        }

    
    def send_text_message(self, message: str, max_tokens: int) -> str:
        """Send a single text message to the LLM and get a text response.
        
        This is a convenience wrapper around send_message for simple string interactions.
        
        Args:
            message: The message to send as a string
            max_tokens: Maximum tokens in response (recommended: 32000)

        Returns:
            The LLM's response as a string
        """
        assert isinstance(message, str), "Message must be a string"
        
        messages = [{"role": "user", "content": message}]
        response = self.send_message(messages, max_tokens)

        return response["content"]
