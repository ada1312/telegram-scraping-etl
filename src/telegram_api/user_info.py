from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerUser
import logging


async def get_user_info(client, user_id):
    try:
        user = await client.get_entity(user_id)
        if user:
            user_info = {
                'id': str(user.id),
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'username': user.username or '',
                'phone': str(user.phone) if user.phone else '',
                'bot': bool(user.bot),
                'verified': bool(user.verified),
                'restricted': bool(user.restricted),
                'scam': bool(user.scam),
                'fake': bool(user.fake),
                'access_hash': str(user.access_hash) if hasattr(user, 'access_hash') else '',
                'bio': user.about if hasattr(user, 'about') else '',
                'bot_info': str(getattr(user, 'bot_info', '')) or '',
            }
            return user_info
        else:
            return None
    except Exception as e:
        logging.error(f"Error getting user info for {user_id}: {e}")
        return None

