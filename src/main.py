import logging
import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
from google.cloud import bigquery
from telegram_api.chat_config import get_chat_configs, update_processed_date
from telegram_api.data_processor import DataProcessor
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
chat_username = os.getenv("CHAT_USERNAME")
logging_level = os.getenv("LOGGING_LEVEL", "INFO").upper()
project_id = os.getenv("PROJECT_ID")
dataset_id = os.getenv("DATASET_ID")
table_chat_config = os.getenv("TABLE_CHAT_CONFIG")
table_chat_history = os.getenv("TABLE_CHAT_HISTORY")
table_chat_info = os.getenv("TABLE_CHAT_INFO")
table_user_info = os.getenv("TABLE_USER_INFO")
backload_start_date = os.getenv("BACKLOAD_START_DATE")
backload_end_date = os.getenv("BACKLOAD_END_DATE")

# Set up logging
logging.basicConfig(level=logging_level)

async def main():
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
        
        chat_configs = await get_chat_configs(bq_client, dataset_id, table_chat_config)
        logging.info(f"Retrieved {len(chat_configs)} chat configs")
        if not chat_configs:
            logging.error("No chat configs found. Exiting.")
            return        
        # Determine dates to process
        if backload_start_date and backload_end_date:
            start_date = datetime.strptime(backload_start_date, "%Y-%m-%d")
            end_date = datetime.strptime(backload_end_date, "%Y-%m-%d")
            dates_to_load = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
            logging.info(f"Backload mode: processing dates from {start_date.date()} to {end_date.date()}")
        else:
            # Daily run mode
            dates_to_load = [datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)]
            logging.info(f"Daily run mode: processing date {dates_to_load[0].date()}")

        new_dates = []
        for date in dates_to_load:
            if date.date() not in chat_configs[0]['dates_to_load']:
                new_dates.append(date.date())
                logging.info(f"Processing chat {chat_username} for date {date.date()}")
                await data_processor.process_chat(chat_username, date)
                logging.info(f"Finished processing chat {chat_username} for date {date.date()}")

        if new_dates:
            await update_processed_date(bq_client, dataset_id, table_chat_config, chat_username, new_dates)
            logging.info(f"Updated chat config with new dates: {new_dates}")

        await data_processor.upload_new_data()
        logging.info("Data processing and upload completed")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
    
    finally:
        await client.disconnect()
        logging.info("Telegram client disconnected")

if __name__ == "__main__":
    asyncio.run(main())