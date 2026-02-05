from pydantic import BaseModel
from typing import List


class RecommendationItem(BaseModel):
    product_id: int
    reason: str | None = None


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
