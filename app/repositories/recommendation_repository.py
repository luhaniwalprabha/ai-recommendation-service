from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation

class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, user_id: int, items: list[int]):
        rec = Recommendation(user_id=user_id, items=items)
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def latest_for_user(self, user_id: int):
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .first()
        )
