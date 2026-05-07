class User:
    """Modèle utilisateur"""
    
    def __init__(self, user_id, name, age, school, major, avatar, bio, badges=None):
        self.id = user_id
        self.name = name
        self.age = age
        self.school = school
        self.major = major
        self.avatar = avatar
        self.bio = bio
        self.badges = badges or []
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("id"),
            name=data.get("name"),
            age=data.get("age"),
            school=data.get("school"),
            major=data.get("major"),
            avatar=data.get("avatar"),
            bio=data.get("bio"),
            badges=data.get("badges", [])
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "school": self.school,
            "major": self.major,
            "avatar": self.avatar,
            "bio": self.bio,
            "badges": self.badges
        }