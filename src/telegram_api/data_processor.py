import logging
from telegram_api.chat_info import get_chat_info
from telegram_api.chat_history import get_chat_history
from bigquery_loader import upload_to_bigquery
from datetime import datetime, time, timezone, timedelta
from telegram_api.chat_config import get_chat_configs
from datetime import datetime, timedelta, timezone


class DataProcessor:
    def __init__(self, client, bq_client, dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info,is_backloading=False):
        """
        Initializes the DataProcessor object with the provided parameters.

        Args:
        - client: The Telegram client object used for API calls.
        - bq_client: The BigQuery client object used for data uploading.
        - dataset_id: The ID of the BigQuery dataset.
        - table_chat_config: The name of the BigQuery table for chat configuration data.
        - table_chat_history: The name of the BigQuery table for chat history data.
        - table_chat_info: The name of the BigQuery table for chat information data.
        - table_user_info: The name of the BigQuery table for user information data.
        """
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
        """
        Initializes the DataProcessor by fetching existing users and chats from BigQuery.
        """
        self._get_existing_users()
        self._get_existing_chats()

    def _get_existing_users(self):
        """
        Fetches existing user IDs from the user information table in BigQuery.
        """
        try:
            query = f"SELECT id FROM `{self.dataset_id}.{self.table_user_info}`"
            query_job = self.bq_client.query(query)
            results = query_job.result()
            self.existing_users = {str(row['id']) for row in results}
            logging.info(f"Fetched {len(self.existing_users)} existing users")
        except Exception as e:
            logging.error(f"Error fetching existing users: {e}", exc_info=True)

    def _get_existing_chats(self):
        """
        Fetches existing chat IDs from the chat information table in BigQuery.
        """
        try:
            query = f"SELECT id FROM `{self.dataset_id}.{self.table_chat_info}`"
            query_job = self.bq_client.query(query)
            results = query_job.result()
            self.existing_chats = {str(row['id']) for row in results}
            logging.info(f"Fetched {len(self.existing_chats)} existing chats")
        except Exception as e:
            logging.error(f"Error fetching existing chats: {e}", exc_info=True)


    async def process_chat(self, username, start_date, end_date, chat_config):
        try:
            chat = await self.client.get_entity(username)
            chat_id = str(chat.id)

            # Ensure start_date and end_date are datetime objects with timezone information
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            # Process one day at a time
            current_date = start_date
            while current_date <= end_date:
                day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                logging.info(f"Processing chat for {username} on {current_date.date()}")

                messages, users = await get_chat_history(
                    self.client, chat, day_start, day_end, 
                    self.bq_client, self.dataset_id, self.table_chat_history
                )

                for user_id, user_info in users.items():
                    user_id_str = str(user_id)
                    if user_id_str not in self.existing_users and user_id_str not in self.new_users:
                        self.new_users[user_id_str] = user_info

                if messages:
                    logging.info(f"Uploading {len(messages)} messages to BigQuery for {username} on {current_date.date()}")
                    await upload_to_bigquery(
                        self.bq_client, messages, 'chat_history', self.dataset_id, 
                        self.table_chat_config, self.table_chat_history, 
                        self.table_chat_info, self.table_user_info
                    )
                else:
                    logging.warning(f"No messages found for {username} on {current_date.date()}")

                # Move to the next day
                current_date += timedelta(days=1)

            logging.info(f"Finished processing chat for {username} from {start_date.date()} to {end_date.date()}")

        except Exception as e:
            logging.error(f"Error processing chat {username} from {start_date} to {end_date}: {e}", exc_info=True)
    
    async def upload_new_data(self):
        """
        Uploads new chat and user data to BigQuery.

        This function uploads the new chat information and user information to their respective tables in BigQuery.
        """
        try:
            if self.new_chats:
                logging.info(f"Uploading {len(self.new_chats)} new chats to BigQuery")
                await upload_to_bigquery(self.bq_client, list(self.new_chats.values()), 'chat_info', self.dataset_id,
                                         self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info)

            if self.new_users:
                logging.info(f"Uploading {len(self.new_users)} new users to BigQuery")
                await upload_to_bigquery(self.bq_client, list(self.new_users.values()), 'user_info', self.dataset_id,
                                         self.table_chat_config, self.table_chat_history, self.table_chat_info, self.table_user_info)
        except Exception as e:
            logging.error(f"Error uploading new data: {e}", exc_info=True)