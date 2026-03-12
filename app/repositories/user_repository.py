from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, age: int, gender: str, interests: list[str]) -> User:
        user = User(age=age, gender=gender, interests=interests)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user