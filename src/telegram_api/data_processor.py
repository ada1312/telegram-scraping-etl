import logging
from datetime import datetime, timedelta
from telegram_api.chat_info import get_chat_info
from telegram_api.chat_history import get_chat_history
from bigquery_loader import upload_to_bigquery

class DataProcessor:
    def __init__(self, client, bq_client, dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info):
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

    async def initialize(self):
        await self._get_existing_users()
        await self._get_existing_chats()

    def _get_existing_users(self):
        query = f"SELECT id FROM `{self.dataset_id}.{self.table_user_info}`"
        query_job = self.bq_client.query(query)
        results = query_job.result()  # This is blocking, but it's okay for this operation
        self.existing_users = {str(row['id']) for row in results}

    def _get_existing_chats(self):
        query = f"SELECT id FROM `{self.dataset_id}.{self.table_chat_info}`"
        query_job = self.bq_client.query(query)
        results = query_job.result()  # This is blocking, but it's okay for this operation
        self.existing_chats = {str(row['id']) for row in results}
   
    async def process_chat(self, username, date):
        chat = await self.client.get_entity(username)
        chat_id = str(chat.id)

        if chat_id not in self.existing_chats and chat_id not in self.new_chats:
            logging.info(f"Fetching chat info for {username}")
            chat_info = await get_chat_info(self.client, chat)
            self.new_chats[chat_id] = chat_info

        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        logging.info(f"Fetching chat history for {username} on {date.date()}")
        messages, users = await get_chat_history(self.client, chat, None, start, end)

        if messages:
            for user_id, user_info in users.items():
                user_id_str = str(user_id)
                if user_id_str not in self.existing_users and user_id_str not in self.new_users:
                    self.new_users[user_id_str] = user_info

            logging.info(f"Uploading chat history to BigQuery for {username} on {date.date()}")
            await upload_to_bigquery(self.bq_client, messages, 'chat_history', self.dataset_id, 
                                     self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info)
        else:
            logging.error(f"Chat history not found for {username} on {date.date()}")

    async def upload_new_data(self):
        if self.new_chats:
            logging.info(f"Uploading {len(self.new_chats)} new chats to BigQuery")
            await upload_to_bigquery(self.bq_client, list(self.new_chats.values()), 'chat_info', self.dataset_id,
                                     self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info)

        if self.new_users:
            logging.info(f"Uploading {len(self.new_users)} new users to BigQuery")
            await upload_to_bigquery(self.bq_client, list(self.new_users.values()), 'user_info', self.dataset_id,
                                     self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info)