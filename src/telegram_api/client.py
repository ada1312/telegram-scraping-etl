import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

def create_client():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    return TelegramClient('session', api_id, api_hash)

async def start_client(client, phone_number):
    await client.start(phone=phone_number)
    return client