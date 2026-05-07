import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProfileController:
    def __init__(self, current_user=None):
        import utils.data as data_module
        if current_user:
            self.user = current_user.copy()
        elif data_module.CURRENT_USER:
            self.user = data_module.CURRENT_USER.copy()
        else:
            self.user = {
                "id": "guest", "name": "Invité", "email": "",
                "school": "—", "major": "—",
                "avatar": "👤", "avatar_color": "#607D8B",
                "bio": "", "posts": [], "badges": []
            }

    def get_current_user(self):
        return self.user

    def update_user(self, updates):
        self.user.update(updates)
        import utils.data as data_module
        if data_module.CURRENT_USER:
            data_module.CURRENT_USER.update(updates)
        try:
            from utils import api_client
            api_client.update_user_profile(self.user)
        except Exception:
            pass
        email = self.user.get("email", "")
        if email and email in data_module.REGISTERED_USERS:
            data_module.REGISTERED_USERS[email].update(updates)
            data_module.save_users()

    def get_shared_resources_count(self):
        return len(self.user.get("posts", []))

    def get_followers_count(self):
        try:
            from utils import api_client
            return api_client.get_followers_count(self.user.get("id", ""))
        except Exception:
            return 0

    def get_following_count(self):
        try:
            from utils import api_client
            return api_client.get_following_count(self.user.get("id", ""))
        except Exception:
            return 0

    def logout(self):
        import utils.data as data_module
        data_module.CURRENT_USER = None
        return True
