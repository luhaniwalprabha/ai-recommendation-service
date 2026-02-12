from sqlalchemy.orm import Session
from app.models.feedback import Feedback

class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, user_id: int, product_id: int, action: str):
        feedback = Feedback(
            user_id=user_id,
            product_id=product_id,
            action=action,
        )
        self.db.add(feedback)
        self.db.commit()
        return feedback
