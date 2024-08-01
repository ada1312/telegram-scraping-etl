import logging
from datetime import datetime
from telegram_api.user_info import get_user_info
from google.cloud import bigquery

def decode_emoji(emoji_string):
    """
    Decode Unicode escape sequences to actual emoji characters.
    """
    return emoji_string.encode('utf-16', 'surrogatepass').decode('utf-16')

async def get_message_reactions(message):
    """
    Retrieve reactions for a given message and format them as a string.
    """
    reaction_str = ""
    if hasattr(message, 'reactions') and message.reactions:
        reactions = []
        for reaction in message.reactions.results:
            if hasattr(reaction.reaction, 'emoticon'):
                emoji = decode_emoji(reaction.reaction.emoticon)
            elif hasattr(reaction.reaction, 'document_id'):
                emoji = f"CustomEmoji:{reaction.reaction.document_id}"
            else:
                emoji = "UnknownEmoji"
            reactions.append(f"{emoji}:{reaction.count}")
        reaction_str = ", ".join(reactions)
    return reaction_str

async def get_chat_history(client, chat, start_date, end_date, bq_client, dataset_id, table_chat_history):
    """
    Retrieves the chat history from a given chat within a specified date range.
    """
    logging.info(f"Fetching chat history for {chat} from {start_date} to {end_date}")
    try:
        messages = []
        users = {}
        
        async for message in client.iter_messages(chat, offset_date=end_date, reverse=False):
            if message.date < start_date:
                logging.info(f"Reached message before start date. Stopping.")
                break
            
            if await message_exists_in_bigquery(message.id, message.chat_id, bq_client, dataset_id, table_chat_history):
                logging.info(f"Message {message.id} already exists in BigQuery. Stopping.")
                break
            
            reactions = await get_message_reactions(message)
            
            # Ensure date fields are properly converted to float
            edit_date_timestamp = message.edit_date.timestamp() if message.edit_date else None
            
            message_data = {
                'id': message.id,
                'date': message.date.strftime('%Y-%m-%d %H:%M:%S %z'),
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
                'entities': None,  # Keeping as None as per original schema
                'mentioned': message.mentioned,
                'post_author': message.post_author if message.post_author is not None else 0,
                'edit_date': edit_date_timestamp,  # Should be a float
                'via_bot': int(message.via_bot_id) if message.via_bot_id is not None else 0,
                'reply_to': {
                    'reply_to_msg_id': message.reply_to.reply_to_msg_id,
                    'reply_to_peer_id': str(message.reply_to.reply_to_peer_id),
                } if message.reply_to else None,
                'reactions': reactions,  # Now a formatted string of emojis and counts
                'fwd_from': None,  # Keeping as None as per original schema
                'grouped_id': int(message.grouped_id) if message.grouped_id is not None else 0,
                'action': str(message.action) if message.action else None,
            }
            messages.append(message_data)
                        
            if hasattr(message.from_id, 'user_id') and message.from_id.user_id not in users:
                user_info = await get_user_info(client, message.from_id.user_id)
                if user_info:
                    users[str(message.from_id.user_id)] = user_info

        logging.info(f"Fetched {len(messages)} messages from {start_date} to {end_date}")
        return messages, users
    except Exception as e:
        logging.error(f"Error getting chat history for {chat}: {e}")
        return [], {}

async def message_exists_in_bigquery(message_id, chat_id, bq_client, dataset_id, table_chat_history):
    query = f"""
    SELECT COUNT(*) as count
    FROM `{dataset_id}.{table_chat_history}`
    WHERE id = @message_id AND chat_id = @chat_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("message_id", "INT64", message_id),
            bigquery.ScalarQueryParameter("chat_id", "INT64", chat_id),
        ]
    )
    
    query_job = bq_client.query(query, job_config=job_config)
    results = query_job.result()
    
    for row in results:
        return row['count'] > 0
    
    return False
