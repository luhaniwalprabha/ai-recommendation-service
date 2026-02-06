from typing import List
from app.schemas.recommendation import RecommendationItem
from app.domain.exceptions import InvalidUserError


class CandidateGenerator:
    """
    Generates candidate product recommendations.
    Deterministic and simple for now.
    """

    def generate(self, user_id: int, limit: int) -> List[RecommendationItem]:
        if user_id <= 0:
            raise InvalidUserError(f"Invalid user_id: {user_id}")

        return []
