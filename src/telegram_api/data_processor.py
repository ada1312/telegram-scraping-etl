import logging
from telegram_api.chat_info import get_chat_info
from telegram_api.chat_history import get_chat_history
from bigquery_loader import upload_to_bigquery
from datetime import datetime, time, timezone, timedelta
from telegram_api.chat_config import get_chat_configs

class DataProcessor:
    def __init__(self, client, bq_client, dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info, is_backloading=False):
        self.client = client
        self.bq_client = bq_client
        self.dataset_id = dataset_id
        self.table_chat_config = table_chat_config
        self.table_chat_history = table_chat_history
        self.table_chat_info = table_chat_info
        self.table_user_info = table_user_info
        self.existing_users = set()
        self.existing_chats = set()
        self.new_users = {}
        self.new_chats = {}
        self.is_backloading = is_backloading

    async def initialize(self):
        await self._get_existing_users()
        await self._get_existing_chats()

    async def _get_existing_users(self):
        try:
            query = f"SELECT CAST(id AS STRING) AS id FROM `{self.dataset_id}.{self.table_user_info}`"
            query_job = self.bq_client.query(query)
            results = query_job.result()
            self.existing_users = {row['id'] for row in results}
            logging.info(f"Fetched {len(self.existing_users)} existing users")
        except Exception as e:
            logging.error(f"Error fetching existing users: {e}", exc_info=True)

    async def _get_existing_chats(self):
        try:
            query = f"SELECT CAST(id AS STRING) AS id FROM `{self.dataset_id}.{self.table_chat_info}`"
            query_job = self.bq_client.query(query)
            results = query_job.result()
            self.existing_chats = {row['id'] for row in results}
            logging.info(f"Fetched {len(self.existing_chats)} existing chats")
        except Exception as e:
            logging.error(f"Error fetching existing chats: {e}", exc_info=True)

    async def process_chat(self, username, start_date, end_date, chat_config):
        try:
            chat = await self.client.get_entity(username)
            chat_id = str(chat.id)

            logging.info(f"Processing chat for {username} from {start_date} to {end_date}")

            messages, users = await get_chat_history(
                self.client, chat, start_date, end_date, 
                self.bq_client, self.dataset_id, self.table_chat_history
            )

            for user_id, user_info in users.items():
                user_id_str = str(user_id)
                if user_id_str not in self.existing_users and user_id_str not in self.new_users:
                    self.new_users[user_id_str] = user_info

            if messages:
                logging.info(f"Uploading {len(messages)} messages to BigQuery for {username}")
                await upload_to_bigquery(
                    self.bq_client, messages, 'chat_history', self.dataset_id, 
                    self.table_chat_config, self.table_chat_history, 
                    self.table_chat_info, self.table_user_info
                )
            else:
                logging.warning(f"No messages found for {username} in the specified date range")

            # Update chat info if needed
            if chat_id not in self.existing_chats and chat_id not in self.new_chats:
                chat_info = await get_chat_info(self.client, chat)
                if chat_info:
                    self.new_chats[chat_id] = chat_info

            logging.info(f"Finished processing chat for {username}")

        except Exception as e:
            logging.error(f"Error processing chat {username}: {e}", exc_info=True)

    async def upload_new_data(self):
        try:
            if self.new_chats:
                logging.info(f"Uploading {len(self.new_chats)} new chats to BigQuery")
                await upload_to_bigquery(
                    self.bq_client, list(self.new_chats.values()), 'chat_info', self.dataset_id,
                    self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info
                )

            if self.new_users:
                logging.info(f"Uploading {len(self.new_users)} new users to BigQuery")
                await upload_to_bigquery(
                    self.bq_client, list(self.new_users.values()), 'user_info', self.dataset_id,
                    self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info
                )
        except Exception as e:
            logging.error(f"Error uploading new data: {e}", exc_info=True)