from pydantic import BaseModel
from typing import List, Optional


class RecommendationItem(BaseModel):
    product_id: int
    score: float | None = None
    reason: Optional[str] = None  # LLM-generated explanation


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
    reranked: bool = False  # whether LLM re-ranking was applied