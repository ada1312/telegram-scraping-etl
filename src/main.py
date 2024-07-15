import logging
import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputPeerChannel, InputPeerUser
from dotenv import load_dotenv
from config import load_config

# Load environment variables
load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
chat_username = os.getenv("CHAT_USERNAME")
sample_size = int(os.getenv("SAMPLE_SIZE"))
logging_level = os.getenv("LOGGING_LEVEL")

async def get_chat_info(client, chat):
    if isinstance(chat, InputPeerChannel):
        full_chat = await client(GetFullChannelRequest(chat))
        return {
            'id': chat.channel_id,
            'title': full_chat.chats[0].title,
            'username': full_chat.chats[0].username,
            'description': full_chat.full_chat.about,
            'members_count': full_chat.full_chat.participants_count,
            'admins_count': full_chat.full_chat.admins_count,
            'kicked_count': full_chat.full_chat.kicked_count,
            'online_count': full_chat.full_chat.online_count,
            'linked_chat_id': full_chat.full_chat.linked_chat_id,
            'slowmode_seconds': full_chat.full_chat.slowmode_seconds,
            'can_view_participants': full_chat.full_chat.can_view_participants,
            'can_set_username': full_chat.full_chat.can_set_username,
            'can_set_stickers': full_chat.full_chat.can_set_stickers,
            'hidden_prehistory': full_chat.full_chat.hidden_prehistory,
            'can_view_stats': full_chat.full_chat.can_view_stats,
            'can_set_location': full_chat.full_chat.can_set_location,
        }
    else:
        return {
            'id': chat.id,
            'title': chat.title,
            'username': chat.username,
            'description': chat.description,
            'members_count': chat.participants_count,
            'linked_chat_id': chat.linked_chat_id,
        }

async def get_user_info(client, user_id):
    try:
        user = await client.get_entity(user_id)
        if isinstance(user, InputPeerUser):
            full_user = await client(GetFullUserRequest(user))
            return {
                'id': user.user_id,
                'first_name': full_user.user.first_name,
                'last_name': full_user.user.last_name,
                'username': full_user.user.username,
                'phone': full_user.user.phone,
                'bot': full_user.user.bot,
                'verified': full_user.user.verified,
                'restricted': full_user.user.restricted,
                'scam': full_user.user.scam,
                'fake': full_user.user.fake,
                'mutual_contact': full_user.user.mutual_contact,
                'access_hash': full_user.user.access_hash,
                'bio': full_user.about,
                'common_chats_count': full_user.common_chats_count,
                'profile_photo': full_user.profile_photo,
                'bot_info': full_user.bot_info,
                'pinned_message': full_user.pinned_msg_id,
                'can_pin_message': full_user.can_pin_message,
            }
        else:
            return {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone': user.phone,
                'bot': user.bot,
                'verified': user.verified,
                'restricted': user.restricted,
                'scam': user.scam,
                'fake': user.fake,
                'access_hash': user.access_hash,
                'bio': user.about,
                'bot_info': user.bot_info,
            }
    except Exception as e:
        logging.error(f"Error getting user info for {user_id}: {e}")
        return None

async def main():
    config = load_config()

    # Set up logging
    logging.basicConfig(level=config.logging_level)

    # Create a TelegramClient instance
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        # Start the client
        await client.start(phone=config.phone_number)
        
        # Get the chat entity
        chat = await client.get_entity(config.chat_username)
        
        # Get chat info
        chat_info = await get_chat_info(client, chat)
        
        # Fetch messages and user info
        messages = []
        users = {}
        async for message in client.iter_messages(chat, limit=config.sample_size):
            message_data = {
                'id': message.id,
                'date': message.date.isoformat(),
                'from_user': message.from_id.user_id if message.from_id else None,
                'text': message.text,
                'sender': message.sender_id,
                'chat_id': message.chat_id,
                'is_reply': bool(message.reply_to_msg_id),
                'views': message.views,
                'forwards': message.forwards,
                'replies': message.replies.replies if message.replies else None,
                'buttons': message.buttons,
                'media': str(message.media) if message.media else None,
                'entities': [str(entity) for entity in message.entities] if message.entities else None,
                'mentioned': message.mentioned,
                'post_author': message.post_author,
                'edit_date': message.edit_date.isoformat() if message.edit_date else None,
                'via_bot': message.via_bot_id,
                'reply_to': {
                    'reply_to_msg_id': message.reply_to.reply_to_msg_id,
                    'reply_to_peer_id': str(message.reply_to.reply_to_peer_id),
                } if message.reply_to else None,
                'reactions': str(message.reactions) if message.reactions else None,
                'fwd_from': str(message.fwd_from) if message.fwd_from else None,
                'grouped_id': message.grouped_id,
                'action': str(message.action) if message.action else None,
            }
            messages.append(message_data)
            
            if message.from_id and message.from_id.user_id not in users:
                user_info = await get_user_info(client, message.from_id.user_id)
                if user_info:
                    users[message.from_id.user_id] = user_info
        
        # Save chat info to JSON file
        with open('chat_info.json', 'w', encoding='utf-8') as f:
            json.dump(chat_info, f, ensure_ascii=False, indent=4)
        
        # Save messages to JSON file
        with open('telegram_messages.json', 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        
        # Save user info to JSON file
        with open('telegram_users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        
        print(f"Chat info saved to chat_info.json")
        print(f"Sample of {len(messages)} messages saved to telegram_messages.json")
        print(f"Information for {len(users)} users saved to telegram_users.json")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        # Disconnect the client
        await client.disconnect()

# Run the main function
asyncio.run(main())