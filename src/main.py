import logging
import os
import asyncio
import argparse
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from dotenv import load_dotenv
from google.cloud import bigquery
from telegram_api.chat_config import get_chat_configs, update_processed_date, ensure_chat_config_exists
from telegram_api.data_processor import DataProcessor

# Load environment variables
load_dotenv()

# Required environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
chat_usernames = os.getenv("CHAT_USERNAMES").split(',')  # Comma-separated list of usernames
sample_size = int(os.getenv("SAMPLE_SIZE", 100))
logging_level = os.getenv("LOGGING_LEVEL", "INFO").upper()
project_id = os.getenv("PROJECT_ID")
dataset_id = os.getenv("DATASET_ID")
table_chat_config = os.getenv("TABLE_CHAT_CONFIG")
table_chat_history = os.getenv("TABLE_CHAT_HISTORY")
table_chat_info = os.getenv("TABLE_CHAT_INFO")
table_user_info = os.getenv("TABLE_USER_INFO")
mode = os.getenv("MODE", "daily")
backload_start_date = os.getenv("BACKLOAD_START_DATE")
backload_end_date = os.getenv("BACKLOAD_END_DATE")

# Set up logging
logging.basicConfig(level=logging_level)

async def main(mode, start_date=None, end_date=None):
    logging.info("Starting Telegram data collection script")
    
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        await client.start(phone=phone_number)
        logging.info("Telegram client started")
        
        bq_client = bigquery.Client(project=project_id)
        logging.info("BigQuery client created")
        
        data_processor = DataProcessor(
            client, bq_client, dataset_id, 
            table_chat_config, table_chat_history, 
            table_chat_info, table_user_info
        )
        await data_processor.initialize()
        logging.info("DataProcessor initialized")
        
        # Ensure chat configs exist for all usernames
        for username in chat_usernames:
            ensure_chat_config_exists(bq_client, dataset_id, table_chat_config, username, username)
        
        chat_configs = await get_chat_configs(bq_client, dataset_id, table_chat_config)
        logging.info(f"Retrieved {len(chat_configs)} chat configs")
        if not chat_configs:
            logging.error("No chat configs found. Exiting.")
            return

        # Determine dates to process
        if mode == 'daily':
            end_date = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            logging.info(f"Daily run mode: processing date {start_date.date()}")
        elif mode == 'backload':
            if not start_date or not end_date:
                logging.error("Backload mode requires both start_date and end_date.")
                return
            start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            logging.info(f"Backload mode: processing dates from {start_date.date()} to {end_date.date()}")

        for username in chat_usernames:
            logging.info(f"Processing chat {username} from {start_date} to {end_date}")
            await data_processor.process_chat(username, start_date, end_date)
            logging.info(f"Finished processing chat {username}")

            # Update processed dates
            processed_dates = [start_date.date() + timedelta(days=i) for i in range((end_date.date() - start_date.date()).days + 1)]
            await update_processed_date(bq_client, dataset_id, table_chat_config, username, processed_dates)
            logging.info(f"Updated chat config for {username} with processed dates: {processed_dates}")

        await data_processor.upload_new_data()
        logging.info("Data processing and upload completed")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
    
    finally:
        await client.disconnect()
        logging.info("Telegram client disconnected")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram data collection script")
    parser.add_argument("mode", choices=['daily', 'backload'], help="Run mode: 'daily' or 'backload'", default=mode, nargs='?')
    parser.add_argument("--start_date", help="Start date for backload (format: YYYY-MM-DD)", default=backload_start_date)
    parser.add_argument("--end_date", help="End date for backload (format: YYYY-MM-DD)", default=backload_end_date)
    
    args = parser.parse_args()
    
    if args.mode == 'backload' and (not args.start_date or not args.end_date):
        parser.error("Backload mode requires both --start_date and --end_date")
    
    asyncio.run(main(args.mode, args.start_date, args.end_date))