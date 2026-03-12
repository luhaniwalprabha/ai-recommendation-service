from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from app.models.product import Product

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
    
    def get_recent_with_details(self, user_id: int, limit: int = 20) -> list[dict]:
        """
        Returns recent feedback enriched with product details — used to build
        the LLM re-ranking prompt so GPT-4 has full context (name, category, price).
        """
        rows = (
            self.db.query(Feedback, Product)
            .join(Product, Feedback.product_id == Product.id)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": feedback.product_id,
                "product_name": product.name,
                "category": product.category,
                "price": product.price,
                "action": feedback.action,
            }
            for feedback, product in rows
        ]
