import logging
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telegram_api.user_info import get_user_info

async def get_chat_history(client, chat, start_date, end_date):
    """
    Retrieves the chat history from a given chat within a specified date range.

    Args:
        client: The Telegram client instance.
        chat: The chat identifier or username.
        start_date: The start date of the chat history (datetime object).
        end_date: The end date of the chat history (datetime object).

    Returns:
        A tuple containing two elements:
        - A list of dictionaries representing the chat messages within the specified date range.
        - A dictionary containing user information for the users who sent the chat messages.

    Raises:
        Exception: If there is an error retrieving the chat history.

    """
    try:
        messages = []
        users = {}
        
        # Convert chat to InputPeer if necessary
        if isinstance(chat, str):
            chat = await client.get_input_entity(chat)
        
        async for message in client.iter_messages(chat, offset_date=end_date, reverse=True):
            if message.date < start_date:
                break
            
            message_data = {
                'id': message.id,
                'date': message.date.timestamp(),
                'from_user': str(message.from_id.user_id) if hasattr(message.from_id, 'user_id') else None,
                'text': message.text,
                'sender': str(message.sender_id) if message.sender_id else None,
                'chat_id': str(message.chat_id),
                'is_reply': bool(message.reply_to_msg_id),
                'views': message.views if message.views is not None else 0,
                'forwards': message.forwards if message.forwards is not None else 0,
                'replies': message.replies.replies if message.replies else 0,
                'buttons': str(message.buttons),
                'media': str(message.media) if message.media else None,
                'entities': None, 
                'mentioned': message.mentioned,
                'post_author': message.post_author if message.post_author is not None else 0,
                'edit_date': message.edit_date.strftime('%Y-%m-%dT%H:%M:%S+00:00') if message.edit_date else None,
                'via_bot': int(message.via_bot_id) if message.via_bot_id is not None else 0,
                'reply_to': {
                    'reply_to_msg_id': message.reply_to.reply_to_msg_id,
                    'reply_to_peer_id': str(message.reply_to.reply_to_peer_id),
                } if message.reply_to else None,
                'reactions': None,  
                'fwd_from': None, 
                'grouped_id': int(message.grouped_id) if message.grouped_id is not None else 0,
                'action': str(message.action) if message.action else None, 
            }
            messages.append(message_data)
            
            if hasattr(message.from_id, 'user_id') and message.from_id.user_id not in users:
                user_info = await get_user_info(client, message.from_id.user_id)
                if user_info:
                    users[str(message.from_id.user_id)] = user_info

        return messages, users
    except Exception as e:
        logging.error(f"Error getting chat history for {chat}: {e}")
        return [], {}