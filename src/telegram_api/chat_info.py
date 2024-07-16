from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputPeerChannel

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