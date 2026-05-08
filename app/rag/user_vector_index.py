from app.rag.user_document_builder import UserDocumentBuilder
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore


class UserVectorIndex:
    def __init__(self):
        self.vector_store = VectorStore(collection_name="user_history")
        self.document_builder = UserDocumentBuilder()
        self.embedding_service = EmbeddingService()
        self.is_built = False

    def build_once(self, interactions):
        if self.is_built:
            return self.vector_store

        documents = []

        for i, interaction in enumerate(interactions):
            text = self.document_builder.build(interaction)
            embedding = self.embedding_service.embed_text(text)

            documents.append({
                "id": f"user_{interaction['user_id']}_{i}",
                "text": text,
                "embedding": embedding,
                "metadata": interaction,
            })

        self.vector_store.add_documents(documents)
        self.is_built = True

        return self.vector_store

    def retrieve(self, query: str, top_k: int = 5):
        query_embedding = self.embedding_service.embed_text(query)

        return self.vector_store.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
        )