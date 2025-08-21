"""Simple Anthropic LLM interface implementation."""

from typing import Optional, List, Dict, Any
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
    
    def send_message(self, message: str, max_tokens: int = 1024) -> str:
        """Send a message to the LLM and get a response.
        
        Args:
            message: The message to send
            max_tokens: Maximum tokens in response (default: 1024)
            
        Returns:
            The LLM's response as a string
        """
        assert isinstance(message, str), "Message must be a string"
        assert isinstance(max_tokens, int), "max_tokens must be an integer"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return response.content[0].text
