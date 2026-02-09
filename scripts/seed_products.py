from app.db.session import SessionLocal
from app.models.product import Product

db = SessionLocal()

products = [
    Product(name="Gold Necklace", category="jewelry", price=1200),
    Product(name="Silver Ring", category="jewelry", price=300),
    Product(name="Diamond Earrings", category="jewelry", price=2500),
]

db.add_all(products)
db.commit()
db.close()
