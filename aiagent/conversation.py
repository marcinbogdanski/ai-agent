"""Conversation management for maintaining chat history with LLM providers."""

class Conversation:
    """Manages conversation history and interaction with LLM providers."""
    
    def __init__(self, provider):
        """Initialize a conversation with a provider.
        
        Args:
            provider: An LLM provider instance with a send_message method
        """        
        self.provider = provider
        self.history: list[dict[str, str]] = []
    
    def send_message(self, message: str) -> str:
        """Send a message and get a response, maintaining conversation history.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response as a string
        """
        assert isinstance(message, str), "Message must be a string"
        
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Send full conversation history to provider
        # Result is dict { "role": "assistant", "content": response_text }
        response = self.provider.send_message(self.history, max_tokens=32000)
        
        # Add assistant response to history
        self.history.append({
            "role": response["role"],
            "content": response["content"]
        })
        
        return response["content"]
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.history = []
    
    def get_history(self) -> list[dict[str, str]]:
        """Get the current conversation history.
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return self.history.copy()

