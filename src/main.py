import logging
import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
from telegram_api.chat_info import get_chat_info
from telegram_api.chat_history import get_chat_info as get_chat_history
from bigquery_loader import upload_to_bigquery
from google.cloud import bigquery

# Load environment variables
load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
chat_username = os.getenv("CHAT_USERNAME")
sample_size = int(os.getenv("SAMPLE_SIZE"))
logging_level = os.getenv("LOGGING_LEVEL")
project_id = os.getenv("PROJECT_ID")

async def main():
    # Set up logging
    logging.basicConfig(level=logging_level)

    # Create a TelegramClient instance
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        # Start the client
        await client.start(phone=phone_number)
        
        # Get the chat entity
        chat = await client.get_entity(chat_username)
        
        # Get chat info
        chat_info = await get_chat_info(client, chat)
        if not chat_info:
            logging.error(f"Chat info not found for {chat_username}")
            return
        
        # Get chat history
        messages, users = await get_chat_history(client, chat, sample_size)
        if not messages or not users:
            logging.error(f"Chat history not found for {chat_username}")
            return

        # Prepare data for BigQuery
        chat_data = [chat_info]
        user_data = list(users.values())
        
        # Create BigQuery client
        bq_client = bigquery.Client(project=project_id)

        # Upload data to BigQuery
        await upload_to_bigquery(bq_client, messages, 'chat_history')
        await upload_to_bigquery(bq_client, chat_data, 'chat_info')
        await upload_to_bigquery(bq_client, user_data, 'user_info')
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        # Disconnect the client
        await client.disconnect()

# Run the main function
asyncio.run(main())