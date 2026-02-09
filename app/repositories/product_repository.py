from sqlalchemy.orm import Session
from app.models.product import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, limit: int = 20):
        return self.db.query(Product).limit(limit).all()

    def create_product(self, product: Product):
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
