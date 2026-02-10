from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    gender = Column(String)
    interests = Column(String)  # comma-separated for now
