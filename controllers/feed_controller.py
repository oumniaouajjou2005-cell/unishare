import sys, os, time as _time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils.data as data_module
from utils import api_client


class FeedController:
    """Contrôleur feed – utilise le serveur réseau avec fallback JSON local."""

    def get_posts(self):
        server_posts = api_client.fetch_posts()
        if server_posts is not None:
            data_module.POSTS = server_posts
        return data_module.POSTS

    def add_post(self, post):
        post.setdefault("id", str(int(_time.time() * 1000)))
        result = api_client.push_post(post)
        if not result:
            data_module.POSTS.insert(0, post)
            data_module.save_posts()

    def update_post(self, updated_post):
        for i, p in enumerate(data_module.POSTS):
            if p.get("id") == updated_post.get("id"):
                data_module.POSTS[i] = updated_post
                break
        data_module.save_posts()

    def delete_post(self, post_to_delete):
        data_module.POSTS = [p for p in data_module.POSTS
                              if p.get("id") != post_to_delete.get("id")]
        data_module.save_posts()

    def like_post(self, post_id):
        user_id = (data_module.CURRENT_USER or {}).get("id", "anon")
        result  = api_client.like_post(post_id, user_id)
        if not result:
            for post in data_module.POSTS:
                if post.get("id") == post_id:
                    if not post.get("liked_by_user", False):
                        post["likes"] = post.get("likes", 0) + 1
                        post["liked_by_user"] = True
                    else:
                        post["likes"] = max(0, post.get("likes", 0) - 1)
                        post["liked_by_user"] = False
                    data_module.save_posts()
                    return True
        return True

    def add_comment(self, post_id, comment):
        result = api_client.add_comment(post_id, comment)
        if not result:
            for post in data_module.POSTS:
                if post.get("id") == post_id:
                    post.setdefault("comments", []).append(comment)
                    data_module.save_posts()
                    return True
        return True
