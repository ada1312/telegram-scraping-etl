import logging
import os
import asyncio
import argparse
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
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
chat_usernames = os.getenv("CHAT_USERNAMES").split(',') 
logging_level = os.getenv("LOGGING_LEVEL", "INFO").upper()
project_id = os.getenv("PROJECT_ID")
dataset_id = os.getenv("DATASET_ID")
table_chat_config = os.getenv("TABLE_CHAT_CONFIG")
table_chat_history = os.getenv("TABLE_CHAT_HISTORY")
table_chat_info = os.getenv("TABLE_CHAT_INFO")
table_user_info = os.getenv("TABLE_USER_INFO")
mode = os.getenv("MODE")
backload_start_date = os.getenv("BACKLOAD_START_DATE")
backload_end_date = os.getenv("BACKLOAD_END_DATE")

session_string = os.getenv("TELEGRAM_SESSION_STRING")

# Set up logging
logging.basicConfig(level=logging_level)

async def main(mode, start_date=None, end_date=None):
    logging.info(f"Starting Telegram data collection script in {mode} mode")
    
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    
    try:
        await client.start(phone=phone_number)
        logging.info("Telegram client started")
        
        bq_client = bigquery.Client(project=project_id)
        logging.info("BigQuery client created")
        
        data_processor = DataProcessor(
            client, bq_client, dataset_id, 
            table_chat_config, table_chat_history, 
            table_chat_info, table_user_info,
            is_backloading=(mode == 'backload')
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
        if mode == 'day_ago':
            today = datetime.now(timezone.utc).date()
            yesterday = today - timedelta(days=1)
            start_date = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_date = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.utc)
        if mode == 'backload':
            if not start_date or not end_date:
                logging.error("Backload mode requires both start_date and end_date.")
                return
            start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            
            # Add this check
            if start_date > datetime.now(timezone.utc) or end_date > datetime.now(timezone.utc):
                logging.error("Start date or end date is in the future. Please check your dates.")
                return
        elif mode == 'recent':
            end_date = datetime.now(timezone.utc)
            
            # Query BigQuery for the actual last processed date
            query = f"""
            SELECT MAX(date) as last_processed_date
            FROM `{dataset_id}.{table_chat_history}`
            """
            query_job = bq_client.query(query)
            results = query_job.result()
            last_processed_date = list(results)[0]['last_processed_date']
            
            if last_processed_date:
                start_date = last_processed_date.replace(tzinfo=timezone.utc) + timedelta(seconds=1)
            else:
                start_date = end_date - timedelta(days=1)  # Default to 1 day ago if no data
            
            # Ensure we're not processing future data
            if start_date > end_date:
                start_date = end_date - timedelta(days=1)

        logging.info(f"Processing data from {start_date} to {end_date}")

        for username in chat_usernames:
            chat_config = chat_configs.get(username)
            if not chat_config:
                logging.warning(f"No chat config found for {username}. Skipping.")
                continue

            await data_processor.process_chat(username, start_date, end_date, chat_config)
            logging.info(f"Finished processing chat {username}")

            # Update processed dates
            if mode == 'recent':
                processed_dates = [end_date.date()]
            else:
                processed_dates = [start_date.date() + timedelta(days=i) for i in range((end_date.date() - start_date.date()).days + 1)]

            await update_processed_date(bq_client, dataset_id, table_chat_config, chat_config['id'], processed_dates)
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
    parser.add_argument("mode", choices=['day_ago', 'backload', 'recent'], help="Run mode: 'day_ago', 'backload', or 'recent'", default=mode, nargs='?')
    parser.add_argument("--start_date", help="Start date for backload (format: YYYY-MM-DD)", default=backload_start_date)
    parser.add_argument("--end_date", help="End date for backload (format: YYYY-MM-DD)", default=backload_end_date)
    
    args = parser.parse_args()
    
    if args.mode == 'backload' and (not args.start_date or not args.end_date):
        parser.error("Backload mode requires both --start_date and --end_date")
    
    asyncio.run(main(args.mode, args.start_date, args.end_date))