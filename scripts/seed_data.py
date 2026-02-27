from app.db.session import SessionLocal
from app.models.product import Product

db = SessionLocal()

products = [
    Product(name="Running Shoes", category="sports", price=2999),
    Product(name="Basketball", category="sports", price=899),
    Product(name="T-Shirt", category="fashion", price=599),
    Product(name="Jeans", category="fashion", price=1999),
    Product(name="Laptop", category="electronics", price=65000),
    Product(name="Headphones", category="electronics", price=1999),
]

db.add_all(products)
db.commit()
db.close()

print("✅ Test data inserted")