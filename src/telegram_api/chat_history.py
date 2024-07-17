import logging
import os
from dotenv import load_dotenv
from telegram_api.user_info import get_user_info

async def get_chat_info(client, chat, sample_size):
    try:
        messages = []
        users = {}
        async for message in client.iter_messages(chat, limit=sample_size):
            message_data = {
                'id': message.id,
                'date': message.date.timestamp(),
                'from_user': message.from_id.user_id if hasattr(message.from_id, 'user_id') else None,
                'text': message.text,
                'sender': message.sender_id,
                'chat_id': message.chat_id,
                'is_reply': bool(message.reply_to_msg_id),
                'views': message.views,
                'forwards': message.forwards,
                'replies': str(message.replies.replies if message.replies else None),
                'buttons': str(message.buttons),
                'media': str(message.media) if message.media else None,
                'entities': None,  # You may need to adjust this based on your actual data
                'mentioned': message.mentioned,
                'post_author': None,  # You may need to adjust this based on your actual data
                'edit_date': message.edit_date.strftime('%Y-%m-%dT%H:%M:%S+00:00') if message.edit_date else None,
                'via_bot': message.via_bot_id,
                'reply_to': {
                    'reply_to_msg_id': message.reply_to.reply_to_msg_id,
                    'reply_to_peer_id': str(message.reply_to.reply_to_peer_id),
                } if message.reply_to else None,
                'reactions': None,  # You may need to adjust this based on your actual data
                'fwd_from': None,  # You may need to adjust this based on your actual data
                'grouped_id': None,  # You may need to adjust this based on your actual data
                'action': None,  # You may need to adjust this based on your actual data
            }
            messages.append(message_data)
            
            if hasattr(message.from_id, 'user_id') and message.from_id.user_id not in users:
                user_info = await get_user_info(client, message.from_id.user_id)
                if user_info:
                    users[message.from_id.user_id] = user_info

        return messages, users
    except Exception as e:
        logging.error(f"Error getting chat info for {chat}: {e}")
        return None, None
