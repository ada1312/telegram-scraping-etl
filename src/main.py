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
mode = os.getenv("MODE", "daily")  # 'daily' or 'backload'
backload_start_date = os.getenv("BACKLOAD_START_DATE")
backload_end_date = os.getenv("BACKLOAD_END_DATE")
update_interval_hours = int(os.getenv("UPDATE_INTERVAL_HOURS", "6"))


def get_chat_configs(bq_client, dataset_id, table_chat_config):
    query = f"""
    SELECT id, username, dates_to_load
    FROM `{dataset_id}.{table_chat_config}`
    """
    query_job = bq_client.query(query)
    results = query_job.result() 
    return [dict(row) for row in results]

def update_chat_config(bq_client, dataset_id, table_chat_config, chat_id, username, new_dates):
    query = f"""
    UPDATE `{dataset_id}.{table_chat_config}`
    SET dates_to_load = ARRAY_CONCAT(dates_to_load, @new_dates)
    WHERE id = @chat_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("chat_id", "STRING", chat_id),
            bigquery.ArrayQueryParameter("new_dates", "DATE", new_dates),
        ]
    )
    query_job = bq_client.query(query, job_config=job_config)
    query_job.result()

async def main():
    logging.basicConfig(level=logging_level)
    
    logging.info("Starting Telegram client setup")
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
        
        chat_configs = get_chat_configs(bq_client, dataset_id, table_chat_config)
        
        if mode == 'backload':
            start_date = datetime.strptime(backload_start_date, "%Y-%m-%d")
            end_date = datetime.strptime(backload_end_date, "%Y-%m-%d")
            dates_to_load = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        else:  # daily mode
            now = datetime.now()
            dates_to_load = [now - timedelta(hours=x) for x in range(0, 24, update_interval_hours)]
        
        for chat_config in chat_configs:
            new_dates = []
            for date in dates_to_load:
                if date.date() not in chat_config['dates_to_load']:
                    new_dates.append(date.date())
                    await data_processor.process_chat(chat_config['username'], date)
            
            if new_dates:
                update_chat_config(bq_client, dataset_id, table_chat_config, chat_config['id'], chat_config['username'], new_dates)
        
        await data_processor.upload_new_data()
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        await client.disconnect()
        logging.info("Telegram client disconnected")

if __name__ == "__main__":
    asyncio.run(main())