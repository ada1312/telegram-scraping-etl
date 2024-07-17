from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerUser
import logging

async def get_user_info(client, user_id):
    try:
        user = await client.get_entity(user_id)
        if user:
            user_info = {
                'id': int(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone': user.phone,
                'bot': user.bot,
                'verified': user.verified,
                'restricted': user.restricted,
                'scam': user.scam,
                'fake': user.fake,
                'access_hash': str(user.access_hash) if hasattr(user, 'access_hash') else None,
                'bio': user.about if hasattr(user, 'about') else None,
                'bot_info': str(getattr(user, 'bot_info', None)),
            }
            return user_info
        else:
            return None
    except Exception as e:
        logging.error(f"Error getting user info for {user_id}: {e}")
        return None

