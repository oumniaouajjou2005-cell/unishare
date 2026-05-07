import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils.data as data_module


class SwipeController:
    def __init__(self):
        self.discussed_users = set()
        self.endless_mode    = True

    def get_users_to_swipe(self):
        current_user = data_module.CURRENT_USER or {}
        current_id   = current_user.get("id", "")

        # Charger les vrais utilisateurs depuis Firebase
        users = []
        try:
            from utils import api_client
            fb_users = api_client.fetch_users()
            for u in fb_users:
                uid = u.get("id", "")
                if uid and uid != current_id:
                    users.append(u)
        except Exception:
            pass

        # Fallback : utilisateurs locaux si Firebase vide
        if not users:
            users = data_module.get_all_swipe_users(current_id)

        if not self.endless_mode:
            users = [u for u in users if u.get("id") not in self.discussed_users]

        return users

    def on_swipe_right(self, user_id):
        if not self.endless_mode:
            self.discussed_users.add(user_id)
        return True

    def on_swipe_left(self, user_id):
        return True

    def save_for_later(self, user):
        already = any(u["id"] == user["id"] for u in data_module.SAVED_FOR_LATER)
        if not already:
            data_module.SAVED_FOR_LATER.append(user)
        return already

    def is_saved_for_later(self, user_id):
        return any(u["id"] == user_id for u in data_module.SAVED_FOR_LATER)

    def get_later_users(self):
        return data_module.SAVED_FOR_LATER

    def remove_from_later(self, user_id):
        data_module.SAVED_FOR_LATER = [
            u for u in data_module.SAVED_FOR_LATER if u["id"] != user_id
        ]

    def reset(self):
        self.discussed_users.clear()
        data_module.SAVED_FOR_LATER.clear()

    def set_endless_mode(self, enabled):
        self.endless_mode = enabled
