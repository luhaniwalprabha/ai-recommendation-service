from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationResponse
from app.cache.redis_client import get
from app.core.logging import get_logger
from app.config import settings
import time
logger = get_logger(__name__)


router = APIRouter(tags=["recommendations"])

@router.post("")
def recommend(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    product_repo = ProductRepository(db)
    rec_repo = RecommendationRepository(db)
    service = RecommendationService(rec_repo, product_repo)
    cache_key = f"recommendations:{user_id}"
    cached = get(cache_key)

    if cached and isinstance(cached, dict) and "items" in cached:
        age = time.time() - cached["generated_at"]
        source = "cache"
        if age > settings.recommendation_soft_ttl_seconds:
            source = "stale"
            background_tasks.add_task(service.generate, user_id)
        return {"source": source, "items": cached["items"]}

    stale_items = rec_repo.latest_items(user_id)
    if stale_items:
        background_tasks.add_task(service.generate, user_id)
        return {"source": "stale", "items": stale_items}

    background_tasks.add_task(service.generate, user_id)
    return {"source": "scheduled", "items": []}



@router.get("/", response_model=RecommendationResponse)
def get_recommendations( user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    items, should_refresh = service.get(user_id)

    if should_refresh:
        background_tasks.add_task(service.generate, user_id)

    return {
        "user_id": user_id,
        "recommendations": [{"product_id": pid} for pid in items],
    }
