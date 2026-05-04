from app.ml.candidate_generator import CandidateGenerator


class VectorCandidateGenerator(CandidateGenerator):
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def generate(self, products, anchor_product_id: int, limit: int = 10):
        product_map = {product.id: product for product in products}
        anchor_product = product_map.get(anchor_product_id)

        if not anchor_product:
            return []

        query = self._build_query(anchor_product)

        results = self.vector_store.search(
            query=query,
            top_k=limit,
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
            ]
            if value
        )