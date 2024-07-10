import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.chat_username = os.getenv("CHAT_USERNAME")
        self.sample_size = int(os.getenv("SAMPLE_SIZE"))
        self.logging_level = os.getenv("LOGGING_LEVEL")

def load_config():
    return Config()