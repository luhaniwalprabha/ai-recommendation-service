from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("")
def submit_feedback(user_id: int, product_id: int, action: str, db: Session = Depends(get_db)):
    repo = FeedbackRepository(db)
    service = FeedbackService(repo)
    return service.submit(user_id, product_id, action)
