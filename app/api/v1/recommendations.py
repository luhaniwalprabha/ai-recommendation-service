from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationResponse, RecommendationItem
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["recommendations"])


def _build_service(db: Session) -> RecommendationService:
    """Central factory so both endpoints share the same wiring."""
    return RecommendationService(
        rec_repo=RecommendationRepository(db),
        product_repo=ProductRepository(db),
        user_repo=UserRepository(db),
        feedback_repo=FeedbackRepository(db),
        debug=True,
        use_dev_data=True,
    )


@router.post("")
def recommend(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    service = _build_service(db)
    items, should_refresh = service.get(user_id)

    if should_refresh:
        background_tasks.add_task(service.generate, user_id)

    source = "cache" if items and not should_refresh else ("stale" if items else "scheduled")
    return {"source": source, "items": items}


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    service = _build_service(db)
    items, should_refresh = service.get(user_id)

    if should_refresh:
        background_tasks.add_task(service.generate, user_id)

    # Normalise items - cache stores dicts, DB fallback may store plain ints
    recommendations = []
    reranked = False
    for item in items:
        if isinstance(item, int):
            recommendations.append(RecommendationItem(product_id=item))
        elif isinstance(item, dict):
            recommendations.append(RecommendationItem(
                product_id=item["product_id"],
                reason=item.get("reason"),
            ))
            if item.get("reason"):
                reranked = True

    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "reranked": reranked,
    }

@router.post("/debug")
def debug_recommendations(user_id: int):
    service = RecommendationService(
        rec_repo = RecommendationRepository(db=None),
        product_repo = ProductRepository(db=None),
        user_repo=None,
        feedback_repo=None,
        debug=True,
        use_dev_data=True,
    )

    debug_data = service.generate(user_id=user_id, debug_mode=True)

    return debug_data