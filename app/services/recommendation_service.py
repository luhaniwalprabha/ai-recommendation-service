from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.cache.redis_client import get, set, delete
from app.core.logging import get_logger
from app.schemas.recommendation import RecommendationItem
from app.config import settings
import time
from app.ml.recommender import ContentBasedRecommender

logger = get_logger(__name__)



class RecommendationService:
    def __init__(
        self,
        rec_repo: RecommendationRepository,
        product_repo: ProductRepository,
    ):
        self.rec_repo = rec_repo
        self.product_repo = product_repo

    def get(self, user_id: int):
        cached = get(user_id)

        if cached and isinstance(cached, dict) and "items" in cached:
            age = time.time() - cached["generated_at"]
            should_refresh = age > settings.recommendation_soft_ttl_seconds
            return cached["items"], should_refresh

        stale = self.rec_repo.latest_items(user_id)
        if stale:
            return stale, True

        return [], True
        
    def _normalize_items(self, items) -> list[RecommendationItem]:
        normalized: list[RecommendationItem] = []
        for item in items:
            if isinstance(item, int):
                normalized.append(RecommendationItem(product_id=item))
            elif isinstance(item, dict):
                normalized.append(RecommendationItem(**item))
        return normalized

    def generate(self, user_id: int):
        logger.info(f"Generating recommendations for user_id={user_id}")
        # cache_key = f"recommendations:{user_id}"
        # lock_key = f"lock:recommendations:{user_id}"

        # prevent duplicate jobs
        if get(user_id):
            return

        set(user_id, "1", ttl=120)

        try:
            products = self.product_repo.list_products()

            if not products:
                return

            recommender = ContentBasedRecommender()
            recommender.fit(products)

            # For demo: use first product as anchor
            anchor_product = products[0]

            product_ids = recommender.recommend_similar(
                anchor_product.id,
                top_k=5
            )


            self.rec_repo.save(user_id, product_ids)
            logger.info(f"Refreshed recommendations for user_id={user_id}")

            payload = {
                "items": product_ids,
                "generated_at": time.time(),
            }

            set(user_id, payload, ttl=3600)

        finally:
            delete(user_id)
