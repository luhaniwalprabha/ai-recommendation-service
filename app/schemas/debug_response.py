from pydantic import BaseModel
from typing import List, Dict, Any


class DebugRecommendationResponse(BaseModel):
    anchor_product_id: int
    raw_candidate_ids: List[int]
    filtered_ids: List[int]
    hybrid_ranked_ids: List[int]
    user_context: List[str]
    final_items: List[Dict[str, Any]]