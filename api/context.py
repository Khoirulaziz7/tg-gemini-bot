"""
The class ChatManager manages all users and their conversations in the
form of a dictionary.

Each user has a ChatConversation instance, which may include multiple
previous conversations of the user (provided by the Pollinations AI API).
"""
from typing import Dict

from .pollinations import ChatConversation


class ChatManager:
    """setting up a basic conversation storage manager"""

    def __init__(self):
        self.chats: Dict[int, ChatConversation] = {}

    def _new_chat(self, history_id: int) -> ChatConversation:
        chat = ChatConversation()
        self.chats[history_id] = chat
        return chat

    def get_chat(self, history_id: int) -> ChatConversation:
        if self.chats.get(history_id) is None:
            return self._new_chat(history_id)
        return self.chats[history_id]