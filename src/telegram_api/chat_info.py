from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputPeerChannel

async def get_chat_info(client, chat):
    """
    Retrieves information about a chat.

    Args:
        client (telethon.TelegramClient): The Telegram client.
        chat (telethon.tl.types.InputPeer): The chat to retrieve information for.

    Returns:
        dict: A dictionary containing the chat information, including the chat ID, name, username, description, members count, and linked chat ID.
    """
    if isinstance(chat, InputPeerChannel):
        full_chat = await client(GetFullChannelRequest(chat))
        return {
            'id': str(chat.channel_id),
            'name': full_chat.chats[0].title or '',
            'username': full_chat.chats[0].username or '',
            'description': full_chat.full_chat.about or '',
            'members_count': int(full_chat.full_chat.participants_count) if full_chat.full_chat.participants_count is not None else 0,
        }
    else:
        return {
            'id': str(chat.id),
            'name': chat.title or '',
            'username': chat.username or '',
            'description': getattr(chat, 'description', '') or '',
            'members_count': int(getattr(chat, 'participants_count', 0)) if getattr(chat, 'participants_count', None) is not None else 0,
        }