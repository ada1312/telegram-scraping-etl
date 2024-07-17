from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputPeerChannel

async def get_chat_info(client, chat):
    if isinstance(chat, InputPeerChannel):
        full_chat = await client(GetFullChannelRequest(chat))
        return {
            'id': str(chat.id),
            'name': full_chat.chats[0].title,
            'username': full_chat.chats[0].username,
            'description': full_chat.full_chat.about,
            'members_count': int(full_chat.full_chat.participants_count) if full_chat.full_chat.participants_count else None,
            'linked_chat_id': full_chat.full_chat.linked_chat_id,
        }
    else:
        return {
            'id': str(chat.id),
            'name': chat.title,
            'username': chat.username,
            'description': getattr(chat, 'description', None),
            'members_count': int(getattr(chat, 'participants_count', None)) if getattr(chat, 'participants_count', None) else None,
            'linked_chat_id': chat.linked_chat_id if hasattr(chat, 'linked_chat_id') else None,
        }