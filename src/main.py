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
logging_level = os.getenv("LOGGING_LEVEL").upper()
project_id = os.getenv("PROJECT_ID")
dataset_id = os.getenv("DATASET_ID")
table_chat_config = os.getenv("TABLE_CHAT_CONFIG")
table_chat_history = os.getenv("TABLE_CHAT_HISTORY")
table_chat_info = os.getenv("TABLE_CHAT_INFO")
table_user_info = os.getenv("TABLE_USER_INFO")

# Main function
async def main():
    # Set up logging
    logging.basicConfig(level=logging_level)
    
    logging.info("Starting Telegram client setup")

    # Create a TelegramClient instance
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        # Start the client
        await client.start(phone=phone_number)
        logging.info("Telegram client started")
        
        # Get the chat entity
        logging.info("Fetching chat entity")
        chat = await client.get_entity(chat_username)
        
        # Get chat info
        logging.info("Fetching chat info")
        chat_info = await get_chat_info(client, chat)
        if not chat_info:
            logging.error("Chat info not found")
            return
        logging.info("Chat info fetched")
        
        # Get chat history
        logging.info("Fetching chat history")
        messages, users = await get_chat_history(client, chat, sample_size)
        if not messages or not users:
            logging.error("Chat history not found")
            return
        logging.info("Chat history fetched")

        # Prepare data for BigQuery
        chat_data = [chat_info]
        user_data = list(users.values())
        
        # Create BigQuery client
        logging.info("Creating BigQuery client")
        bq_client = bigquery.Client(project=project_id)

        # Upload data to BigQuery
        logging.info("Uploading chat history to BigQuery")
        await upload_to_bigquery(bq_client, messages, 'chat_history',dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info)
        
        logging.info("Uploading chat info to BigQuery")
        await upload_to_bigquery(bq_client, chat_data, 'chat_info',dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info)
        
        logging.info("Uploading user info to BigQuery")
        await upload_to_bigquery(bq_client, user_data, 'user_info',dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info)
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        # Disconnect the client
        await client.disconnect()
        logging.info("Telegram client disconnected")

# Run the main function
asyncio.run(main())
