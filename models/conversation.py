from datetime import datetime

class Message:
    """Modèle message"""
    
    def __init__(self, sender_id, text, timestamp=None):
        self.sender_id = sender_id
        self.text = text
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self):
        return {
            "sender_id": self.sender_id,
            "text": self.text,
            "timestamp": self.timestamp.strftime("%H:%M")
        }

class Conversation:
    """Modèle conversation entre deux utilisateurs"""
    
    def __init__(self, user1_id, user2_id):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.messages = []
    
    def add_message(self, sender_id, text):
        message = Message(sender_id, text)
        self.messages.append(message)
        return message
    
    def get_messages(self):
        return [msg.to_dict() for msg in self.messages]