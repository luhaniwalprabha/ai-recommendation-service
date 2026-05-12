from app.ml.hybrid_ranker import HybridRanker


class FakeProduct:
    def __init__(self, id, name, description, rating):
        self.id = id
        self.name = name
        self.category = "Jewelry"
        self.brand = None
        self.description = description
        self.tags = []
        self.attributes = {}
        self.review_summary = ""
        self.average_rating = rating


def test_hybrid_ranker_boosts_preference_match():
    products = [
        FakeProduct(1, "Diamond Ring", "Luxury premium ring", 4.9),
        FakeProduct(2, "Silver Chain", "Minimal lightweight silver chain", 4.2),
    ]

    ranked = HybridRanker().rank(
        products=products,
        user_preferences=["minimal", "lightweight"],
    )

    assert ranked[0].id == 2