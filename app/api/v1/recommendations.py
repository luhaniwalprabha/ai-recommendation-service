from fastapi import APIRouter
from app.schemas.recommendation import RecommendationResponse
from app.domain.recommendation import generate_recommendations

router = APIRouter()


@router.get("/", response_model=RecommendationResponse)
def get_recommendations(user_id: int, limit: int = 5):
    recommendations = generate_recommendations(user_id=user_id, limit=limit)

    return RecommendationResponse(
        user_id=user_id,
        recommendations=recommendations,
    )
