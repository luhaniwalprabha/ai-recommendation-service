from sqlalchemy import Column, Integer, String, Float, Text, JSON
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    price = Column(Float)
    description = Column(Text, nullable=True)
    brand = Column(String, nullable=True)
    attributes = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    review_summary = Column(Text, nullable=True)
    average_rating = Column(Float, nullable=True)
    inventory_status = Column(String, default="available")
