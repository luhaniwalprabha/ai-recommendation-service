from app.rag.product_document_builder import ProductDocumentBuilder
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore


class ProductIndexBuilder:
    def __init__(
        self,
        document_builder: ProductDocumentBuilder | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.document_builder = document_builder or ProductDocumentBuilder()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore(collection_name="products")

    def build(self, products):
        documents = []

        for product in products:
            text = self.document_builder.build(product)
            embedding = self.embedding_service.embed_text(text)

            documents.append({
                "id": f"product_{product.id}",
                "text": text,
                "embedding": embedding,
                "metadata": {
                    "product_id": product.id,
                    "category": getattr(product, "category", None),
                    "brand": getattr(product, "brand", None),
                },
            })

        self.vector_store.add_documents(documents)

        return self.vector_store