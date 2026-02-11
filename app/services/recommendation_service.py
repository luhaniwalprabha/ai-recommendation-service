from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.cache.redis_client import get, set


class RecommendationService:
    def __init__(
        self,
        rec_repo: RecommendationRepository,
        product_repo: ProductRepository,
    ):
        self.rec_repo = rec_repo
        self.product_repo = product_repo

    def generate(self, user_id: int):
        cache_key = f"recommendations:{user_id}"

        cached = get(cache_key)
        if cached:
            return {"source": "cache", "items": cached}

        products = self.product_repo.list_products(limit=5)
        product_ids = [p.id for p in products]

        # Save in DB
        self.rec_repo.save(user_id, product_ids)

        # Save in cache (1 hour TTL)
        set(cache_key, product_ids, ttl=3600)

        return {"source": "db", "items": product_ids}