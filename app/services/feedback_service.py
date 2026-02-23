from app.repositories.feedback_repository import FeedbackRepository
from app.cache.redis_client import delete
from app.core.logging import get_logger
logger = get_logger(__name__)


class FeedbackService:
    def __init__(self, feedback_repo: FeedbackRepository):
        self.feedback_repo = feedback_repo

    def submit(self, user_id: int, product_id: int, action: str):
        logger.info(f"Generating recommendations for user_id={user_id}")
        feedback = self.feedback_repo.save(user_id, product_id, action)

        # Invalidate recommendation cache
        cache_key = f"recommendations:{user_id}"
        delete(cache_key)

        return {"status": "feedback recorded", "cache_invalidated": True}
