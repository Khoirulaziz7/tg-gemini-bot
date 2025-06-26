from typing import Dict

import requests
from md2tgmd import escape

from .config import BOT_TOKEN, send_message_log, send_photo_log, unnamed_user, unnamed_group
from .printLog import send_log

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, **kwargs):
    """send text message"""
    payload = {
        "chat_id": chat_id,
        "text": escape(text),
        "parse_mode": "MarkdownV2",
        **kwargs,
    }
    r = requests.post(f"{TELEGRAM_API}/sendMessage", data=payload)
    print(f"Sent message: {text} to {chat_id}")
    send_log(f"{send_message_log}\n```json\n{str(r)}```")
    return r


def send_imageMessage(chat_id, text, imageID):
    """send image message"""
    payload = {
        "chat_id": chat_id,
        "caption": escape(text),
        "parse_mode": "MarkdownV2",
        "photo": imageID
    }
    r = requests.post(f"{TELEGRAM_API}/sendPhoto", data=payload)
    print(f"Sent imageMessage: {text} to {chat_id}")
    send_log(f"{send_photo_log}\n```json\n{str(r)}```")
    return r


def check_channel_membership(user_id: int, channel_username: str) -> bool:
    """Check if user is a member of the specified channel"""
    try:
        # Add @ if not present and not an ID
        if not channel_username.startswith('@') and not channel_username.startswith('-'):
            channel_username = f"@{channel_username}"
        
        url = f"{TELEGRAM_API}/getChatMember"
        params = {
            "chat_id": channel_username,
            "user_id": user_id
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                status = data.get("result", {}).get("status")
                # User is considered joined if they are member, administrator, or creator
                return status in ["member", "administrator", "creator"]
        
        return False
    except Exception as e:
        send_log(f"Error checking channel membership: {e}")
        return False


class Update:
    def __init__(self, update: Dict) -> None:
        self.update = update
        self.from_id = update["message"]["from"]["id"]
        self.chat_id = update["message"]["chat"]["id"]
        self.from_type = update["message"]["chat"]["type"]
        self.is_group: bool = self._is_group()
        self.type = self._type()
        self.text = self._text()
        self.file_id = self._file_id()
        #self.user_name = update["message"]["from"]["username"]
        self.user_name = update["message"]["from"].get("username", f" [{unnamed_user}](tg://openmessage?user_id={self.from_id})")
        self.group_name = update["message"]["chat"].get("username", f" [{unnamed_group}](tg://openmessage?chat_id={str(self.chat_id)[4:]})")
        self.message_id: int = update["message"]["message_id"]

    def _is_group(self):
        if self.from_type == "supergroup":
            return True
        return False

    def _type(self):
        if "text" in self.update["message"]:
            text = self.update["message"]["text"]
            if text.startswith("/") and not text.startswith("/new"):
                return "command"
            return "text"
        elif "photo" in self.update["message"]:
            return "photo"
        else:
            return ""

    def _text(self):
        if self.type == "text":
            return self.update["message"]["text"]
        elif self.type == "command":
            text = self.update["message"]["text"]
            command = text[1:]
            return command
        return ""

    def _file_id(self):
        if self.type == "photo":
            return self.update["message"]["photo"][-1]["file_id"]
        return ""