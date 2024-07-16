import logging
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerUser

async def get_user_info(client, user_id):
    try:
        user = await client.get_entity(user_id)
        if isinstance(user, InputPeerUser):
            full_user = await client(GetFullUserRequest(user))
            return {
                'id': user.user_id,
                'first_name': full_user.user.first_name,
                'last_name': full_user.user.last_name,
                'username': full_user.user.username,
                'phone': full_user.user.phone,
                'bot': full_user.user.bot,
                'verified': full_user.user.verified,
                'restricted': full_user.user.restricted,
                'scam': full_user.user.scam,
                'fake': full_user.user.fake,
                'mutual_contact': full_user.user.mutual_contact,
                'access_hash': full_user.user.access_hash,
                'bio': full_user.about,
                'common_chats_count': full_user.common_chats_count,
                'profile_photo': full_user.profile_photo,
                'bot_info': full_user.bot_info,
                'pinned_message': full_user.pinned_msg_id,
                'can_pin_message': full_user.can_pin_message,
            }
        else:
            return {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone': user.phone,
                'bot': user.bot,
                'verified': user.verified,
                'restricted': user.restricted,
                'scam': user.scam,
                'fake': user.fake,
                'access_hash': user.access_hash,
                'bio': user.about,
                'bot_info': user.bot_info,
            }
    except Exception as e:
        logging.error(f"Error getting user info for {user_id}: {e}")
        return None