from app.rag.product_document_builder import ProductDocumentBuilder
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore


def build_product_index(products):
    document_builder = ProductDocumentBuilder()
    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    documents = []

    for product in products:
        text = document_builder.build(product)
        embedding = embedding_service.embed_text(text)

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

    vector_store.add_documents(documents)

    return vector_store