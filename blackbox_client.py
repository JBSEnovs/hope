"""
BlackboxAI Client Tool

A standalone tool to test the BlackboxAI API directly from the command line.
This allows testing the API without running the full Flask application.
"""

import sys
import argparse
from agents.blackbox_ai import BlackboxAI
import uuid

def main():
    """Main function to run the BlackboxAI client tool"""
    parser = argparse.ArgumentParser(description='BlackboxAI Client Tool')
    parser.add_argument('--model', type=str, default='blackboxai', 
                        help='Model to use (blackboxai, gpt-4o, claude-sonnet-3.5, gemini-pro)')
    parser.add_argument('--conversation', type=str, default=None,
                        help='Conversation ID for continuing a conversation')
    parser.add_argument('--list-models', action='store_true',
                        help='List available models')
    parser.add_argument('--message', type=str, default=None,
                        help='Message to send to BlackboxAI')
    
    args = parser.parse_args()
    
    # Initialize the BlackboxAI agent
    blackbox = BlackboxAI(model=args.model)
    
    # List models if requested
    if args.list_models:
        models = blackbox.get_available_models()
        print("Available models:")
        for model in models:
            current = " (current)" if model == blackbox.model else ""
            print(f"- {model}{current}")
        return
    
    # If no message is provided, enter interactive mode
    if not args.message:
        conversation_id = args.conversation or str(uuid.uuid4())
        print(f"BlackboxAI Interactive Mode (Model: {blackbox.model}, Conversation: {conversation_id})")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("Type 'model:NAME' to change the model.")
        
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting conversation.")
                    break
                    
                # Check for model change command
                if user_input.lower().startswith('model:'):
                    new_model = user_input.split(':', 1)[1].strip()
                    if blackbox.change_model(new_model):
                        print(f"Model changed to {new_model}")
                    else:
                        print(f"Invalid model: {new_model}")
                        print(f"Available models: {', '.join(blackbox.get_available_models())}")
                    continue
                
                # Send message to BlackboxAI
                print("\nBlackboxAI is thinking...")
                response = blackbox.chat(user_input, conversation_id)
                
                print("\nBlackboxAI:", response)
                
            except KeyboardInterrupt:
                print("\nExiting conversation.")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
    else:
        # Simple one-off message mode
        try:
            response = blackbox.chat(args.message, args.conversation)
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 