from app.ml.candidate_generator import CandidateGenerator
from app.ml.recommender import ContentBasedRecommender


class TfidfCandidateGenerator(CandidateGenerator):
    def generate(self, products, anchor_product_id: int, limit: int = 10):
        recommender = ContentBasedRecommender()
        recommender.fit(products)
        return recommender.recommend_similar(
            product_id=anchor_product_id,
            top_k=limit,
        )