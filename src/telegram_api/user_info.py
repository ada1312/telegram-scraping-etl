from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerUser
import logging

async def get_user_info(client, user_id):
    try:
        user = await client.get_entity(user_id)
        user_info = {
            'id': str(user_id),
            'first_name': None,
            'last_name': None,
            'username': None,
            'phone': None,
            'bot': None,
            'verified': None,
            'restricted': None,
            'scam': None,
            'fake': None,
            'access_hash': None,
            'bio': None,
            'bot_info': None,
        }
        
        if user:
            user_info.update({
                'first_name': user.first_name or None,
                'last_name': user.last_name or None,
                'username': user.username or None,
                'phone': str(user.phone) if user.phone else None,
                'bot': bool(user.bot),
                'verified': bool(user.verified),
                'restricted': bool(user.restricted),
                'scam': bool(user.scam),
                'fake': bool(user.fake),
                'access_hash': str(user.access_hash) if hasattr(user, 'access_hash') else None,
                'bio': user.about if hasattr(user, 'about') else None,
                'bot_info': str(getattr(user, 'bot_info', '')) or None,
            })
        
        return user_info
    except Exception as e:
        return {
            'id': str(user_id),
            'first_name': None,
            'last_name': None,
            'username': None,
            'phone': None,
            'bot': None,
            'verified': None,
            'restricted': None,
            'scam': None,
            'fake': None,
            'access_hash': None,
            'bio': None,
            'bot_info': None,
        }