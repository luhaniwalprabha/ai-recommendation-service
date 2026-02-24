from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationResponse
from app.domain.recommendation import generate_recommendations
from app.domain.exceptions import InvalidUserError, RecommendationError
from app.cache.redis_client import get, set
from app.core.logging import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["recommendations"])

@router.post("")
def recommend(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    product_repo = ProductRepository(db)
    rec_repo = RecommendationRepository(db)
    service = RecommendationService(rec_repo, product_repo)

    background_tasks.add_task(service.generate, user_id)

    return {"status": "scheduled"}




@router.get("/", response_model=RecommendationResponse)
def get_recommendations(user_id: int, db: Session = Depends(get_db),):

    product_repo = ProductRepository(db)
    rec_repo = RecommendationRepository(db)
    service = RecommendationService(rec_repo, product_repo)

    items = service.get(user_id)

    return {
    "user_id": user_id,
    "recommendations": items
    }