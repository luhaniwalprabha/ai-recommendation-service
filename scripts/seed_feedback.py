from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.feedback import Feedback

def seed_feedback():
    db: Session = SessionLocal()

    feedback_data = [
        {"user_id": 1, "product_id": 1, "action": "click"},
        {"user_id": 1, "product_id": 2, "action": "like"},
        {"user_id": 1, "product_id": 3, "action": "click"},
        {"user_id": 2, "product_id": 2, "action": "click"},
        {"user_id": 2, "product_id": 4, "action": "dismiss"},
    ]

    for f in feedback_data:
        feedback = Feedback(**f)
        db.add(feedback)

    db.commit()
    db.close()

    print("✅ Feedback seeded successfully")


if __name__ == "__main__":
    seed_feedback()