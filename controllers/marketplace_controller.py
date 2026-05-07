import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.product import Product


class MarketplaceController:
    """Contrôleur pour la marketplace"""

    def __init__(self):
        self.products = []
        self.cart = []
        self.current_user_id = "current_user"
        self.current_user_name = "Moi"
    
    def get_all_products(self):
        """Retourne tous les produits"""
        return [p.to_dict() for p in self.products]
    
    def get_products_by_category(self, subject):
        """Filtre les produits par matière"""
        return [p.to_dict() for p in self.products if p.subject.lower() == subject.lower()]
    
    def get_products_by_university(self, university):
        """Filtre les produits par université"""
        return [p.to_dict() for p in self.products if p.university.lower() == university.lower()]
    
    def get_product_by_id(self, product_id):
        """Retourne un produit par son ID"""
        for p in self.products:
            if p.id == product_id:
                return p.to_dict()
        return None
    
    def add_product(self, product_dict):
        """Ajoute un produit vendu par l'utilisateur courant"""
        # S'assurer que le vendeur est l'utilisateur courant
        product_dict["seller_id"] = self.current_user_id
        product_dict["seller_name"] = self.current_user_name
        product_dict["rating"] = 0
        product_dict["downloads"] = 0
        
        new_product = Product.from_dict(product_dict)
        self.products.append(new_product)
    
    def get_my_products(self):
        """Récupère les produits de l'utilisateur courant"""
        return [p.to_dict() for p in self.products if p.seller_id == self.current_user_id]
    
    def add_to_cart(self, product):
        """Ajoute un produit au panier"""
        # Vérifier si déjà dans le panier
        for item in self.cart:
            if item["id"] == product["id"]:
                return
        self.cart.append(product)
    
    def remove_from_cart(self, product_id):
        """Retire un produit du panier"""
        self.cart = [p for p in self.cart if p["id"] != product_id]
    
    def get_cart(self):
        """Retourne le contenu du panier"""
        return self.cart
    
    def get_cart_total(self):
        """Retourne le total du panier"""
        return sum(p.get("price", 0) for p in self.cart)
    
    def purchase_cart(self):
        """Simule un achat du panier"""
        if not self.cart:
            return {"success": False, "error": "Panier vide"}
        
        total = self.get_cart_total()
        
        # Mettre à jour les téléchargements des produits
        for item in self.cart:
            for p in self.products:
                if p.id == item["id"]:
                    p.downloads += 1
        
        # Vider le panier
        purchased_items = self.cart.copy()
        self.cart.clear()
        
        return {"success": True, "total": total, "items": purchased_items}
    
    def search_products(self, query):
        """Recherche des produits par mot-clé"""
        query_lower = query.lower()
        results = []
        for p in self.products:
            if (query_lower in p.title.lower() or 
                query_lower in p.description.lower() or
                query_lower in p.subject.lower() or
                query_lower in p.major.lower()):
                results.append(p.to_dict())
        return results
    
    def add_review(self, product_id, rating, comment, user_name):
        """Ajoute un avis sur un produit"""
        # Pour la démo, on ne stocke pas les avis, mais on met à jour la note moyenne
        for p in self.products:
            if p.id == product_id:
                # Calculer nouvelle note moyenne (simulé)
                old_rating = p.rating
                new_rating = (old_rating + rating) / 2
                p.rating = round(new_rating, 1)
                return True
        return False