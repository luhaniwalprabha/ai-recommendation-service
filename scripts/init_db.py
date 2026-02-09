from app.db.session import engine
from app.db.base import Base
from app.models.product import Product

Base.metadata.create_all(bind=engine)
