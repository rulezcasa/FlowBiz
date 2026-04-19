# cli_chat.py
import sys
from orchestrator.router import orchestrate
import asyncio

async def main():
    print("=== Welcome to Profile Salons : (CLI Chat Testbed) ===")
    print("Type 'exit' to quit.\n")


    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat. Goodbye!")
            sys.exit(0)
        
        response=await orchestrate('9035790945',user_input)
        # if isinstance(response, list) and all(isinstance(item, dict) and 'text' in item for item in response):
        #     texts = [item['text'] for item in response]
        # else:
        #     texts = response  # fallback to original
        texts=response
        print(f"Bot: {texts}\n")

if __name__ == "__main__":
    asyncio.run(main())