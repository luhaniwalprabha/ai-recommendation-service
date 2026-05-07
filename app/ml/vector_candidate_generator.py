from app.ml.candidate_generator import CandidateGenerator
from app.rag.embedding_service import EmbeddingService
import logging
logger = logging.getLogger(__name__)


class VectorCandidateGenerator(CandidateGenerator):
    def __init__(self, vector_store, embedding_service: EmbeddingService | None = None):
        self.vector_store = vector_store
        self.embedding_service = embedding_service or EmbeddingService()

    def generate(self, products, anchor_product_id: int, limit: int = 10):
        product_map = {product.id: product for product in products}
        anchor_product = product_map.get(anchor_product_id)

        if not anchor_product:
            return []

        query = self._build_query(anchor_product)
        query_embedding = self.embedding_service.embed_text(query)

        logger.info(f"Vector search query: {query}")
        results = self.vector_store.search_by_embedding(
            query_embedding=query_embedding,
            top_k=limit,
        )
        logger.info(f"Vector search returned {len(results)} results")
        
        for r in results[:5]:
        logger.info(
            f"Candidate product_id={r['metadata']['product_id']} score={r['score']}"
        )

        return [
            result["metadata"]["product_id"]
            for result in results
            if "metadata" in result and "product_id" in result["metadata"]
        ]

    def _build_query(self, product) -> str:
        return " ".join(
            str(value)
            for value in [
                getattr(product, "name", None),
                getattr(product, "category", None),
                getattr(product, "brand", None),
                getattr(product, "description", None),
                getattr(product, "tags", None),
                getattr(product, "review_summary", None),
            ]
            if value
        )