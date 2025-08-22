"""Simple turn-by-turn chat interface using Conversation and AnthropicProvider."""

import os
import sys
import json
from typing import Optional

from aiagent.providers.anthropic import AnthropicProvider
from aiagent.conversation import Conversation


def print_welcome() -> None:
    """Print welcome message and instructions."""
    print("=" * 60)
    print("Welcome to the AI Chat Interface")
    print("=" * 60)
    print("\nCommands:")
    print("  /quit or /exit - End the chat")
    print("  /clear - Clear conversation history")
    print("  /history - Show conversation history")
    print("  /help - Show this help message")
    print("\nType your message and press Enter to chat.")
    print("-" * 60)


def get_api_key() -> Optional[str]:
    """Get API key from environment variable.
    
    Returns:
        API key string or None if not found
    """
    api_key = os.environ.get("MY_ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: MY_ANTHROPIC_API_KEY environment variable not set.")
        print("Please set your Anthropic API key before running this script.")
    return api_key


def handle_command(command: str, conversation: Conversation) -> bool:
    """Handle special commands.
    
    Args:
        command: The command to handle (with leading /)
        conversation: The conversation instance
        
    Returns:
        True if should continue chatting, False if should exit
    """
    command = command.lower()
    
    if command in ["/quit", "/exit"]:
        print("\nGoodbye! Thank you for chatting.")
        return False
    
    elif command == "/clear":
        conversation.clear_history()
        print("\nConversation history cleared.")
        
    elif command == "/history":
        history = conversation.get_history()
        if history:
            print("\n=== Conversation History ===")
            print(json.dumps(history, indent=2))
            print("=== End of History ===")
        else:
            print("\nNo conversation history yet.")
            
    elif command == "/help":
        print_welcome()
        
    else:
        print(f"\nUnknown command: {command}")
        print("Type /help for available commands.")
    
    return True


def main() -> None:
    """Main chat loop."""
    # Get API key
    api_key = get_api_key()
    if not api_key:
        sys.exit(1)
    
    # Initialize provider and conversation
    try:
        # Using a cheaper model for cost efficiency - you can change this
        provider = AnthropicProvider(api_key=api_key, model="claude-3-haiku-20240307")
        conversation = Conversation(provider)
    except Exception as e:
        print(f"Error initializing chat: {e}")
        sys.exit(1)
    
    # Print welcome message
    print_welcome()
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check if empty input
            if not user_input:
                continue
            
            # Check for commands
            if user_input.startswith("/"):
                if not handle_command(user_input, conversation):
                    break
                continue
            
            # Send message and get response
            print("\nAssistant: ", end="", flush=True)
            response = conversation.send_message(user_input)
            print(response)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Use /quit to exit properly.")
            continue
            
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again or use /quit to exit.")


if __name__ == "__main__":
    main()
