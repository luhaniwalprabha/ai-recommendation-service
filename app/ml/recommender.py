import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.product_ids = []
        self.tfidf_matrix = None

    def fit(self, products):
        """
        products: list of Product objects
        """
        documents = [
            f"{p.name} {p.category or ''}"
            for p in products
        ]

        self.product_ids = [p.id for p in products]
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def recommend_similar(self, product_id, top_k=5):
        if self.tfidf_matrix is None:
            return []

        if product_id not in self.product_ids:
            return []

        idx = self.product_ids.index(product_id)

        similarities = cosine_similarity(
            self.tfidf_matrix[idx],
            self.tfidf_matrix
        ).flatten()

        # exclude itself
        similarities[idx] = -1

        top_indices = similarities.argsort()[-top_k:][::-1]

        return [self.product_ids[i] for i in top_indices]