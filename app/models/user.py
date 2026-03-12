from sqlalchemy import Column, Integer, String
from app.db.base import Base
from sqlalchemy.dialects.postgresql import ARRAY

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    gender = Column(String)
    interests = Column(ARRAY(String), default=list)
