from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.start(phone=phone_number)
    print(client.session.save())