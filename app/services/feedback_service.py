from app.repositories.feedback_repository import FeedbackRepository
from app.cache.redis_client import delete

class FeedbackService:
    def __init__(self, feedback_repo: FeedbackRepository):
        self.feedback_repo = feedback_repo

    def submit(self, user_id: int, product_id: int, action: str):
        feedback = self.feedback_repo.save(user_id, product_id, action)

        # Invalidate recommendation cache
        cache_key = f"recommendations:{user_id}"
        delete(cache_key)

        return {"status": "feedback recorded", "cache_invalidated": True}
