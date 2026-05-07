class Product:
    """Modèle produit pour la marketplace"""
    
    def __init__(self, product_id, title, description, price, seller_id, seller_name, 
                 file_type, subject, university, major, rating=0, downloads=0):
        self.id = product_id
        self.title = title
        self.description = description
        self.price = price
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.file_type = file_type  # PDF, Video, Document, etc.
        self.subject = subject
        self.university = university
        self.major = major
        self.rating = rating
        self.downloads = downloads
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            price=data.get("price"),
            seller_id=data.get("seller_id"),
            seller_name=data.get("seller_name"),
            file_type=data.get("file_type"),
            subject=data.get("subject"),
            university=data.get("university"),
            major=data.get("major"),
            rating=data.get("rating", 0),
            downloads=data.get("downloads", 0)
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "file_type": self.file_type,
            "subject": self.subject,
            "university": self.university,
            "major": self.major,
            "rating": self.rating,
            "downloads": self.downloads
        }