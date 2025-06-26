from .config import ALLOWED_USERS, ADMIN_ID, AUCH_ENABLE, ALLOWED_GROUPS, REQUIRED_CHANNEL, BOT_TOKEN
from .telegram import check_channel_membership


def is_authorized(is_group, from_id: int, user_name: str, chat_id, group_name) -> bool:
    if AUCH_ENABLE == "0":
        return True
    if is_group:
        if str(group_name).lower() in ALLOWED_GROUPS or str(chat_id) in ALLOWED_GROUPS:
            return True
    else:
        if str(user_name).lower() in ALLOWED_USERS or str(from_id) in ALLOWED_USERS:
            return True
    return False


def is_admin(from_id: int) -> bool:
    if str(from_id) == ADMIN_ID:
        return True
    return False


def check_channel_join_required(user_id: int) -> bool:
    """Check if user has joined the required channel"""
    if not REQUIRED_CHANNEL:
        return True  # No channel requirement set
    
    return check_channel_membership(user_id, REQUIRED_CHANNEL)