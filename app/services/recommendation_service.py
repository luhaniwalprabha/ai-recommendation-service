from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository

class RecommendationService:
    def __init__(
        self,
        rec_repo: RecommendationRepository,
        product_repo: ProductRepository,
    ):
        self.rec_repo = rec_repo
        self.product_repo = product_repo

    def generate(self, user_id: int):
        products = self.product_repo.list_products(limit=5)
        product_ids = [p.id for p in products]

        return self.rec_repo.save(user_id, product_ids)
