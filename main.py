import logging
import os
import json
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
chat_username = os.getenv("CHAT_USERNAME")
sample_size = int(os.getenv("SAMPLE_SIZE"))
logging_level = os.getenv("LOGGING_LEVEL")

# Set up logging
logging.basicConfig(level=logging_level)

async def main():
    # Create a TelegramClient instance
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        # Start the client
        await client.start(phone=phone_number)
        
        # Get the chat entity
        chat = await client.get_entity(chat_username)
        
        # Fetch messages
        messages = []
        async for message in client.iter_messages(chat, limit=sample_size):
            messages.append({
                'id': message.id,
                'date': message.date.isoformat(),
                'from_user': message.from_id.user_id if message.from_id else None,
                'text': message.text,
            })
        
        # Save to JSON file
        with open('telegram_sample.json', 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        
        print(f"Sample of {len(messages)} messages saved to telegram_sample.json")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Disconnect the client
        await client.disconnect()

# Run the main function
asyncio.run(main())