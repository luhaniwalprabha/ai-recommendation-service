class ExplanationGenerator:
    def generate(
        self,
        product,
        user_preferences: list[str] | None = None,
        user_context: list[str] | None = None,
    ) -> str:
        user_preferences = user_preferences or []
        user_context = user_context or []

        matched_preferences = self._matched_preferences(product, user_preferences)

        if matched_preferences:
            return (
                f"Matches your preference for "
                f"{', '.join(matched_preferences[:2])}."
            )

        rating = getattr(product, "average_rating", None)
        if rating and rating >= 4.5:
            return "Highly rated and relevant to your recent interest."

        category = getattr(product, "category", None)
        if category:
            return f"Similar to products you recently explored in {category}."

        return "Recommended based on your recent activity."

    def _matched_preferences(self, product, preferences: list[str]) -> list[str]:
        text = self._product_text(product).lower()

        return [
            pref
            for pref in preferences
            if pref.lower() in text
        ]

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