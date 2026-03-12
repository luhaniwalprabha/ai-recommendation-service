"""
Generation pipeline:
1. ContentBasedRecommender → top 10 ML candidates
2. Filter out already-seen products
3. If user has >= 3 feedback interactions → LLM re-ranks with reasons
4. Otherwise → use original ML order, no reasons
5. Save top 5 to DB + Redis cache
"""

from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.cache.redis_client import get as cache_get, set as cache_set, delete as cache_delete, acquire_lock
from app.core.logging import get_logger
from app.schemas.recommendation import RecommendationItem
from app.config import settings
from app.ml.recommender import ContentBasedRecommender
from app.ml.llm_reranker import LLMReranker
import time

logger = get_logger(__name__)

TOP_CANDIDATES = 10
FINAL_COUNT = 5


class RecommendationService:
    def __init__(
        self,
        rec_repo: RecommendationRepository,
        product_repo: ProductRepository,
        user_repo: UserRepository | None = None,
        feedback_repo: FeedbackRepository | None = None,
    ):
        self.rec_repo = rec_repo
        self.product_repo = product_repo
        self.user_repo = user_repo
        self.feedback_repo = feedback_repo

    def get(self, user_id: int):
        """
        Returns (items, should_refresh) where items is a list of dicts:
        [{"product_id": int, "reason": str | None}, ...]
        """
        cache_key = f"recommendations:{user_id}"
        cached = cache_get(cache_key)

        if cached and isinstance(cached, dict) and "items" in cached:
            age = time.time() - cached["generated_at"]
            should_refresh = age > settings.recommendation_soft_ttl_seconds
            return cached["items"], should_refresh

        stale = self.rec_repo.latest_items(user_id)
        if stale:
            return stale, True

        return [], True

    def generate(self, user_id: int):
        logger.info(f"Generating recommendations for user_id={user_id}")

        lock_key = f"lock:recs:{user_id}"

        if not acquire_lock(lock_key, ttl=120):
            logger.info(f"Skipping generation for user_id={user_id} - lock held")
            return

        try:
            # ----------------------------------------------------------------
            # Step 1: ML candidate generation
            # ----------------------------------------------------------------
            products = self.product_repo.list_products(limit=200)

            if not products:
                logger.warning(f"No products found - skipping for user_id={user_id}")
                return

            recommender = ContentBasedRecommender()
            recommender.fit(products)

            user_product_ids = self.rec_repo.get_user_recent_products(user_id)

            anchor_product = None
            if user_product_ids:
                anchor_id = user_product_ids[0]
                anchor_product = next((p for p in products if p.id == anchor_id), None)

            if anchor_product is None:
                anchor_product = products[0]

            candidate_ids = recommender.recommend_similar(
                anchor_product.id,
                top_k=TOP_CANDIDATES,
            )

            # Filter seen products
            seen = set(user_product_ids)
            filtered_ids = [pid for pid in candidate_ids if pid not in seen]
            if not filtered_ids:
                filtered_ids = candidate_ids  # nothing new - show anyway

            # Map IDs back to Product objects for LLM context
            product_map = {p.id: p for p in products}
            candidate_products = [product_map[pid] for pid in filtered_ids if pid in product_map]

            # ----------------------------------------------------------------
            # Step 2: LLM re-ranking (only if user has enough feedback history)
            # ----------------------------------------------------------------
            reranked = False
            final_items: list[dict] = []

            if self.user_repo and self.feedback_repo:
                user = self.user_repo.get(user_id)
                raw_feedback = self.feedback_repo.get_recent_with_details(user_id, limit=20)

                reranker = LLMReranker()
                llm_result = reranker.rerank(
                    candidates=candidate_products,
                    user=user,
                    feedback=raw_feedback,
                )

                if llm_result:
                    final_items = llm_result[:FINAL_COUNT]
                    reranked = True
                    logger.info(f"LLM re-ranking applied for user_id={user_id}")

            # Fall back to ML order if LLM skipped or failed
            if not final_items:
                final_items = [
                    {"product_id": p.id, "reason": None}
                    for p in candidate_products[:FINAL_COUNT]
                ]
                logger.info(f"Using ML order for user_id={user_id} (no LLM re-ranking)")

            # ----------------------------------------------------------------
            # Step 3: Persist to DB and cache
            # ----------------------------------------------------------------
            item_ids = [item["product_id"] for item in final_items]
            self.rec_repo.save(user_id, item_ids)

            payload = {
                "items": final_items,   # list of {"product_id": int, "reason": str|None}
                "reranked": reranked,
                "generated_at": time.time(),
            }

            cache_key = f"recommendations:{user_id}"
            cache_set(cache_key, payload, ttl=3600)

            logger.info(
                f"Saved recommendations for user_id={user_id} "
                f"(reranked={reranked}, count={len(final_items)})"
            )

        finally:
            cache_delete(lock_key)

    def _normalize_items(self, items) -> list[RecommendationItem]:
        normalized: list[RecommendationItem] = []
        for item in items:
            if isinstance(item, int):
                normalized.append(RecommendationItem(product_id=item))
            elif isinstance(item, dict):
                normalized.append(RecommendationItem(
                    product_id=item["product_id"],
                    reason=item.get("reason"),
                ))
        return normalized