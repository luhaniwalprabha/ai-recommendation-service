from app.rag.product_index_builder import ProductIndexBuilder
from app.rag.vector_store import VectorStore


class ProductVectorIndex:
    def __init__(self):
        self.vector_store = VectorStore(collection_name="products")
        self.is_built = False

    def build_once(self, products):
        if self.is_built:
            return self.vector_store

        builder = ProductIndexBuilder(
            vector_store=self.vector_store,
        )

        self.vector_store = builder.build(products)
        self.is_built = True

        return self.vector_store

    def rebuild(self, products):
        self.vector_store = VectorStore(collection_name="products")
        builder = ProductIndexBuilder(
            vector_store=self.vector_store,
        )

        self.vector_store = builder.build(products)
        self.is_built = True

        return self.vector_store