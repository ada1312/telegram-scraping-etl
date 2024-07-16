async def get_messages(client, chat, limit):
    messages = []
    async for message in client.iter_messages(chat, limit=limit):
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
    return messages