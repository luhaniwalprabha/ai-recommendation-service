from typing import List
from app.schemas.recommendation import RecommendationItem
from app.services.candidate_generator import CandidateGenerator


def generate_recommendations(user_id: int, limit: int) -> List[RecommendationItem]:
    generator = CandidateGenerator()
    candidates = generator.generate(user_id=user_id, limit=limit)

    return candidates


