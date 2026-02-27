from app.db.session import SessionLocal
from app.repositories.product_repository import ProductRepository
from app.ml.recommender import ContentBasedRecommender

db = SessionLocal()
repo = ProductRepository(db)

products = repo.list_products()

rec = ContentBasedRecommender()
rec.fit(products)

anchor = products[0]

print("ANCHOR:", anchor.name)
print("SIMILAR:", rec.recommend_similar(anchor.id))