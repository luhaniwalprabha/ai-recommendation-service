from app.db.session import SessionLocal
from app.models.product import Product

def seed_data():
    db = SessionLocal()
    try:
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
        print("✅ Test data inserted")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()