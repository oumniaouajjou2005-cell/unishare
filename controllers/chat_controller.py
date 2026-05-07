import sys, os, time as _time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils.data as data_module
from utils import api_client


class ChatController:
    def __init__(self):
        self._cache = {}   # conv_id → [messages]

    @staticmethod
    def _conv_id(id1, id2):
        return "_".join(sorted([str(id1), str(id2)]))

    def create_conversation(self, user1_id, user2_id):
        cid = self._conv_id(user1_id, user2_id)
        if cid not in self._cache:
            self._cache[cid] = []
        return cid

    def send_message(self, conversation_id, sender_id, text):
        msg = {
            "conv_id":  conversation_id,
            "sender":   sender_id,
            "text":     text,
            "time":     _time.strftime("%H:%M"),
            "id":       str(int(_time.time() * 1000)),
        }
        result = api_client.send_message(msg)
        if not result:
            # Fallback local
            data_module.ALL_MESSAGES.append(msg)
            data_module.save_messages()
        self._cache.setdefault(conversation_id, []).append(msg)
        return True

    def get_messages(self, conversation_id):
        server_msgs = api_client.fetch_messages(conversation_id)
        if server_msgs is not None:
            self._cache[conversation_id] = server_msgs
            return server_msgs
        # Fallback : messages locaux
        local = [m for m in data_module.ALL_MESSAGES
                 if m.get("conv_id") == conversation_id]
        self._cache[conversation_id] = local
        return local
