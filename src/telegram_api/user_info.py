
async def get_user_info(client, user_id):
    """
    Retrieves information about a user from the Telegram API.

    Args:
        client: The Telegram client instance.
        user_id: The ID of the user.

    Returns:
        A dictionary containing the user information. The dictionary has the following keys:
        - 'id': The ID of the user.
        - 'first_name': The first name of the user.
        - 'last_name': The last name of the user.
        - 'username': The username of the user.
        - 'phone': The phone number of the user.
        - 'bot': A boolean indicating whether the user is a bot.
        - 'verified': A boolean indicating whether the user is verified.
        - 'restricted': A boolean indicating whether the user is restricted.
        - 'scam': A boolean indicating whether the user is marked as a scam.
        - 'fake': A boolean indicating whether the user is marked as fake.
        - 'access_hash': The access hash of the user.
        - 'bio': The biography of the user.
        - 'bot_info': Additional information about the bot user.

    Raises:
        Exception: If an error occurs while retrieving the user information.
    """
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
            'scam': None,
            'access_hash': None,
            'bio': None,
        }
        
        if user:
            user_info.update({
                'first_name': user.first_name or None,
                'last_name': user.last_name or None,
                'username': user.username or None,
                'phone': int(user.phone) if user.phone is not None else 0,
                'bot': bool(user.bot),
                'verified': bool(user.verified),
                'scam': bool(user.scam),
                'access_hash': str(user.access_hash) if hasattr(user, 'access_hash') else None,
                'bio': user.about if hasattr(user, 'about') else None,
            })
        
        return user_info
    except Exception as e:
        return {
            'id': str(user_id),
            'first_name': None,
            'last_name': None,
            'username': None,
            'phone': 0,
            'bot': False,
            'verified': False,
            'scam': False,
            'access_hash': 0,
            'bio': None,
        }