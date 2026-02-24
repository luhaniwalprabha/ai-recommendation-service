from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.cache.redis_client import get, set, delete
from app.core.logging import get_logger
from app.schemas.recommendation import RecommendationItem

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
        cache_key = f"recommendations:{user_id}"

        cached = get(cache_key)
        if cached:
            logger.info(f"Cache hit for user {user_id}")
            return self._normalize_items(cached)

        logger.info(f"Cache miss for user {user_id}")

        stale = self.rec_repo.latest_items(user_id)

        if stale:
            logger.info("Returning stale DB recommendations")
            return self._normalize_items(stale)

        return []

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
        cache_key = f"recommendations:{user_id}"
        lock_key = f"lock:recommendations:{user_id}"

        # prevent duplicate jobs
        if get(lock_key):
            return

        set(lock_key, "1", ttl=120)

        try:
            cached = get(cache_key)
            if cached:
                logger.info(f"Cache hit for user_id={user_id}")
                return

            products = self.product_repo.list_products(limit=5)
            product_ids = [p.id for p in products]

            self.rec_repo.save(user_id, product_ids)
            logger.info(f"Saved recommendations for user_id={user_id}")

            set(cache_key, product_ids, ttl=3600)

        finally:
            delete(lock_key)
