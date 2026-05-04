class VectorStore:
    def add_documents(self, documents: list[dict]) -> None:
        """
        documents format:
        [
            {
                "id": "product_1",
                "text": "...",
                "metadata": {"product_id": 1}
            }
        ]
        """
        raise NotImplementedError

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Returns nearest documents.
        """
        raise NotImplementedError