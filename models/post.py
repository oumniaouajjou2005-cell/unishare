class Post:
    """Modèle publication feed"""
    
    def __init__(self, post_id, user_name, user_avatar, content, likes=0, comments=0):
        self.id = post_id
        self.user_name = user_name
        self.user_avatar = user_avatar
        self.content = content
        self.likes = likes
        self.comments = comments
        self.liked_by_current_user = False
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data.get("id"),
            user_name=data.get("user"),
            user_avatar=data.get("user_avatar", "👤"),
            content=data.get("content"),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0)
        )
    
    def like(self):
        if not self.liked_by_current_user:
            self.likes += 1
            self.liked_by_current_user = True
    
    def unlike(self):
        if self.liked_by_current_user:
            self.likes -= 1
            self.liked_by_current_user = False