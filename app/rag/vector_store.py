import chromadb


class VectorStore:
    def __init__(self, collection_name: str = "products"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(self, documents: list[dict]) -> None:
        if not documents:
            return

        self.collection.add(
            ids=[doc["id"] for doc in documents],
            documents=[doc["text"] for doc in documents],
            embeddings=[doc["embedding"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents],
        )

    def search_by_embedding(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        documents = []

        for i, doc_id in enumerate(results["ids"][0]):
            documents.append({
                "id": doc_id,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i],
            })

        return documents