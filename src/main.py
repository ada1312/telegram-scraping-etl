import logging
import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
from telegram_api.chat_info import get_chat_info
from telegram_api.chat_history import get_chat_history
from bigquery_loader import upload_to_bigquery
from google.cloud import bigquery
from telegram_api.chat_config import upsert_chat_config, get_chat_configs
from telegram_api.data_processor import DataProcessor
from datetime import datetime, timedelta
import argparse

# Load environment variables
load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
logging_level = os.getenv("LOGGING_LEVEL").upper()
project_id = os.getenv("PROJECT_ID")
dataset_id = os.getenv("DATASET_ID")
table_chat_config = os.getenv("TABLE_CHAT_CONFIG")
table_chat_history = os.getenv("TABLE_CHAT_HISTORY")
table_chat_info = os.getenv("TABLE_CHAT_INFO")
table_user_info = os.getenv("TABLE_USER_INFO")

def parse_args():
    parser = argparse.ArgumentParser(description="Telegram chat backup script")
    parser.add_argument("--start_date", type=str, required=True, help="Start date for backup (YYYY-MM-DD)")
    parser.add_argument("--interval_hours", type=int, default=12, help="Backup interval in hours")
    return parser.parse_args()

def generate_date_range(start_date, interval_hours):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.now()
    current = start
    while current < end:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(hours=interval_hours)

async def update_chat_configs(bq_client, dataset_id, table_chat_config, chat_configs, dates):
    for chat in chat_configs:
        await upsert_chat_config(bq_client, dataset_id, table_chat_config, chat['id'], chat['username'], dates)

async def main():
    args = parse_args()
    logging.basicConfig(level=logging_level)
    
    logging.info("Starting Telegram client setup")
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        await client.start(phone=phone_number)
        logging.info("Telegram client started")
        
        bq_client = bigquery.Client(project=project_id)
        logging.info("BigQuery client created")
        
        # Generate date range
        dates = list(generate_date_range(args.start_date, args.interval_hours))
        
        # Get existing chat configurations
        chat_configs = await get_chat_configs(bq_client, dataset_id, table_chat_config)
        
        # Update chat configurations with new dates
        await update_chat_configs(bq_client, dataset_id, table_chat_config, chat_configs, dates)
        
        # Initialize DataProcessor
        data_processor = DataProcessor(client, bq_client, dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info)
        await data_processor.initialize()
        
        # Process chats
        for chat_config in chat_configs:
            await data_processor.process_chat(chat_config)
        
        # Upload new data
        await data_processor.upload_new_data()
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        await client.disconnect()
        logging.info("Telegram client disconnected")

if __name__ == "__main__":
    asyncio.run(main())
