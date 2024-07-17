from dataclasses import dataclass
import os

@dataclass
class Config:
    api_id: str
    api_hash: str
    phone_number: str
    chat_username: str
    sample_size: int
    logging_level: str
    project_id: str
    dataset_id: str
    chat_info_table_id: str
    messages_table_id: str
    users_table_id: str

def load_config():
    return Config(
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH"),
        phone_number=os.getenv("PHONE_NUMBER"),
        chat_username=os.getenv("CHAT_USERNAME"),
        sample_size=int(os.getenv("SAMPLE_SIZE")),
        logging_level=os.getenv("LOGGING_LEVEL"),
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        dataset_id=os.getenv("BIGQUERY_DATASET_ID"),
        chat_info_table_id=os.getenv("CHAT_INFO_TABLE_ID"),
        messages_table_id=os.getenv("MESSAGES_TABLE_ID"),
        users_table_id=os.getenv("USERS_TABLE_ID"),
    )