class EmbeddingService:
    def embed_text(self, text: str) -> list[float]:
        """
        Converts a single text into an embedding vector.
        We will implement this on Day 4.
        """
        raise NotImplementedError

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Converts multiple texts into embedding vectors.
        """
        return [self.embed_text(text) for text in texts]