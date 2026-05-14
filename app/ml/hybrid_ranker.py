class HybridRanker:
    def rank(
        self,
        products: list,
        user_context: list[str] | None = None,
        user_preferences: list[str] | None = None,
        return_scores: bool = False,
        limit: int = 10,
    ) -> list:
        user_context = user_context or []
        user_preferences = user_preferences or []

        scored = []

        for product in products:
            score = 0.0

            score += self._rating_score(product)
            score += self._preference_score(product, user_preferences)
            score += self._context_score(product, user_context)

            score_details = {
                "rating": self._rating_score(product),
                "preference": self._preference_score(product, user_preferences),
                "context": self._context_score(product, user_context),
            }

            total_score = sum(score_details.values())

            scored.append((total_score, product, score_details))

        scored.sort(key=lambda item: item[0], reverse=True)
        
        if return_scores:
            return [
                {
                    "product_id": product.id,
                    "score": total,
                    "breakdown": details,
                }
                for total, product, details in scored[:limit]
            ]

        return [product for total, product, details in scored[:limit]]

    def _rating_score(self, product) -> float:
        rating = getattr(product, "average_rating", None)
        if rating is None:
            return 0.0
        return min(float(rating) / 5.0, 1.0)

    def _preference_score(self, product, preferences: list[str]) -> float:
        text = self._product_text(product).lower()
        score = 0.0

        for pref in preferences:
            if pref.lower() in text:
                score += 0.5

        return score

    def _context_score(self, product, user_context: list[str]) -> float:
        text = self._product_text(product).lower()
        score = 0.0

        for context in user_context:
            for word in context.lower().split():
                if word in text:
                    score += 0.05

        return min(score, 1.0)

    def _product_text(self, product) -> str:
        return " ".join(
            str(value)
            for value in [
                getattr(product, "name", ""),
                getattr(product, "category", ""),
                getattr(product, "brand", ""),
                getattr(product, "description", ""),
                getattr(product, "tags", ""),
                getattr(product, "attributes", ""),
                getattr(product, "review_summary", ""),
            ]
            if value
        )