from fastapi import APIRouter, HTTPException
from app.schemas.recommendation import RecommendationResponse
from app.domain.recommendation import generate_recommendations
from app.domain.exceptions import InvalidUserError, RecommendationError

router = APIRouter()


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
