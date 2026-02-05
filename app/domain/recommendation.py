from typing import List
from app.schemas.recommendation import RecommendationItem


def generate_recommendations(user_id: int, limit: int) -> List[RecommendationItem]:
    """
    Core recommendation logic.
    For now, returns an empty list.
    """
    return []
