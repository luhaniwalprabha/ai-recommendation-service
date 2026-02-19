from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationResponse
from app.domain.recommendation import generate_recommendations
from app.domain.exceptions import InvalidUserError, RecommendationError
from app.cache.redis_client import get



router = APIRouter(tags=["recommendations"])

@router.post("")
def recommend(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    cache_key = f"recommendations:{user_id}"

    if get(cache_key):
        return {"status": "ready", "source": "cache"}

    product_repo = ProductRepository(db)
    rec_repo = RecommendationRepository(db)
    service = RecommendationService(rec_repo, product_repo)

    # try stale DB result
    stale = rec_repo.latest_items(user_id)

    if stale:
        background_tasks.add_task(service.generate, user_id)
        return {"source": "stale", "items": stale}

    # no stale data → schedule generation
    background_tasks.add_task(service.generate, user_id)
    return {"status": "processing"}




@router.get("/", response_model=RecommendationResponse)
def get_recommendations(user_id: int, limit: int = 5):
    try:
        recommendations = generate_recommendations(user_id=user_id, limit=limit)

        return RecommendationResponse(
            user_id=user_id,
            recommendations=recommendations,
        )

    except InvalidUserError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except RecommendationError:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recommendations",
        )
