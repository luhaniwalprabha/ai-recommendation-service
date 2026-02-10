from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = Column(JSON)  # list of product IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
