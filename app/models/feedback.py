from sqlalchemy import Column, Integer, ForeignKey, String
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    action = Column(String)  # click, like, dismiss
