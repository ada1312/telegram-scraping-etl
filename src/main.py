import asyncio
import logging
from config import load_config
from telegram_api.client import create_client, start_client
from telegram_api.chat_info import get_chat_info
from telegram_api.user_info import get_user_info
from telegram_api.message_handlers import get_messages
from writer_bigquery import async_load

#here we are importing the functions from the telegram_api package
async def main():
    config = load_config()

    # Set up logging
    logging.basicConfig(level=config.logging_level)

    # Create and start the client
    client = create_client()
    
    try:
        await start_client(client, config.phone_number)
        
        # Get the chat entity
        chat = await client.get_entity(config.chat_username)
        
        # Get chat info
        chat_info = await get_chat_info(client, chat)
        
        # Fetch messages and user info
        messages = await get_messages(client, chat, config.sample_size)
        users = {}
        for message in messages:
            if message['from_user'] and message['from_user'] not in users:
                user_info = await get_user_info(client, message['from_user'])
                if user_info:
                    users[message['from_user']] = user_info
        
        # Upload data to BigQuery
        chat_info_success = await async_load([chat_info], config.chat_info_table_id)
        messages_success = await async_load(messages, config.messages_table_id)
        users_success = await async_load(list(users.values()), config.users_table_id)
        
        if chat_info_success:
            print(f"Chat info successfully uploaded to BigQuery table {config.chat_info_table_id}")
        else:
            print(f"Failed to upload chat info to BigQuery table {config.chat_info_table_id}")
        
        if messages_success:
            print(f"Sample of {len(messages)} messages successfully uploaded to BigQuery table {config.messages_table_id}")
        else:
            print(f"Failed to upload messages to BigQuery table {config.messages_table_id}")
        
        if users_success:
            print(f"Information for {len(users)} users successfully uploaded to BigQuery table {config.users_table_id}")
        else:
            print(f"Failed to upload user information to BigQuery table {config.users_table_id}")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        # Disconnect the client
        await client.disconnect()

# Run the main function
asyncio.run(main())