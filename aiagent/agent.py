

from aiagent.conversation import Conversation
from aiagent.providers.anthropic import AnthropicProvider


class Agent:
    def __init__(self, api_key: str):
        assert isinstance(api_key, str), "API key must be a string"
        self.api_key = api_key

        self.provider = AnthropicProvider(api_key=self.api_key)
        self.conversation = Conversation(provider=self.provider)

    def send_message(self, message: str) -> str:
        """Send a message to the LLM and get a response."""
        assert isinstance(message, str), "Message must be a string"
        return self.conversation.send_message(message)
