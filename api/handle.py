"""
All the chat that comes through the Telegram bot gets passed to the
handle_message function. This function checks out if the user has the
green light to chat with the bot. Once that's sorted, it figures out if
the user sent words or an image and deals with it accordingly.

For text messages, it fires up the ChatManager class that keeps track of
the back-and-forth with that user.

Images are not supported as Pollinations AI text endpoint doesn't support
image analysis.
"""

from .auth import is_authorized, check_channel_join_required
from .command import excute_command
from .context import ChatManager
from .telegram import Update, send_message
from .printLog import send_log
from .config import *

chat_manager = ChatManager()


def handle_message(update_data):
    update = Update(update_data)
    if update.is_group :
        log = f"{event_received}\n@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`\n{the_content_sent_is}\n{update.text}\n```json\n{update_data}```"
    else:
        log = f"{event_received}\n@{update.user_name} id:`{update.from_id}`\n{the_content_sent_is}\n{update.text}\n```json\n{update_data}```"
    send_log(log)
    
    # Check if user has joined required channel (skip for groups and commands)
    if not update.is_group and update.type != "command":
        if REQUIRED_CHANNEL and not check_channel_join_required(update.from_id):
            channel_display = REQUIRED_CHANNEL
            if not channel_display.startswith('@') and not channel_display.startswith('-'):
                channel_display = f"@{channel_display}"
            
            send_message(update.from_id, channel_join_required_info.format(channel=channel_display))
            log = f"@{update.user_name} id:`{update.from_id}`{not_joined_channel},{the_content_sent_is}\n{update.text}"
            send_log(log)
            return

    authorized = is_authorized(update.is_group, update.from_id, update.user_name,  update.chat_id, update.group_name)

    if update.type == "command":
        response_text = excute_command(update.from_id, update.text, update.from_type, update.chat_id)
        if response_text!= "":
            send_message(update.chat_id, response_text)
            if update.is_group :
                log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}"
            else:
                log = f"@{update.user_name} id:`{update.from_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}"
            send_log(log)

    elif not authorized:
        if update.is_group:
            send_message(update.chat_id, f"{group_no_permission_info}\nID:`{update.chat_id}`")
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{no_rights_to_use},{the_content_sent_is}\n{update.text}"
        else:
            send_message(
            update.from_id, f"{user_no_permission_info}\nID:`{update.from_id}`")
            log = f"@{update.user_name} id:`{update.from_id}`{no_rights_to_use},{the_content_sent_is}\n{update.text}"
        send_log(log)
        return

    elif update.type == "text":
        if update.is_group and GROUP_MODE == "2":
            history_id = update.from_id
        else:
            history_id = update.chat_id
        chat = chat_manager.get_chat(history_id)
        anwser = chat.send_message(update.text)
        extra_text = (
            f"\n\n{prompt_new_info}" if chat.history_length >= prompt_new_threshold*2 else ""
        )
        response_text = f"{anwser}{extra_text}"
        send_message(update.chat_id, response_text)
        dialogueLogarithm = int(chat.history_length/2)
        if update.is_group:
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}\n{the_logarithm_of_historical_conversations_is}{dialogueLogarithm}"
        else:
            log = f"@{update.user_name} id:`{update.from_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}\n{the_logarithm_of_historical_conversations_is}{dialogueLogarithm}"
        send_log(log)

    elif update.type == "photo":
        # Images are not supported with Pollinations AI text endpoint
        send_message(update.chat_id, image_not_supported_info, reply_to_message_id=update.message_id)
        
        if update.is_group:
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}` sent image - not supported"
        else:
            log = f"@{update.user_name} id:`{update.from_id}` sent image - not supported"
        send_log(log)

    else:
        send_message(
            update.chat_id, f"{unable_to_recognize_content_sent}\n\n/help")
        if update.is_group:
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{send_unrecognized_content}"
        else:
            log = f"@{update.user_name} id:`{update.from_id}`{send_unrecognized_content}"
        send_log(log)