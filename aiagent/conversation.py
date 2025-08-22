"""Conversation management for maintaining chat history with LLM providers."""

from typing import List, Dict, Optional, Any


class Conversation:
    """Manages conversation history and interaction with LLM providers."""
    
    def __init__(self, provider: Any):
        """Initialize a conversation with a provider.
        
        Args:
            provider: An LLM provider instance with a send_message method
        """
        assert hasattr(provider, 'send_message'), "Provider must have send_message method"
        
        self.provider = provider
        self.history: List[Dict[str, str]] = []
    
    def send_message(self, message: str, max_tokens: int = 1024) -> str:
        """Send a message and get a response, maintaining conversation history.
        
        Args:
            message: The user's message
            max_tokens: Maximum tokens in response (default: 1024)
            
        Returns:
            The assistant's response as a string
        """
        assert isinstance(message, str), "Message must be a string"
        assert isinstance(max_tokens, int), "max_tokens must be an integer"
        
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Send full conversation history to provider
        # Result is dict { "role": "assistant", "content": response_text }
        response = self.provider.send_message(self.history, max_tokens=max_tokens)
        
        # Add assistant response to history
        self.history.append({
            "role": response["role"],
            "content": response["content"]
        })
        
        return response["content"]
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history.
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return self.history.copy()

