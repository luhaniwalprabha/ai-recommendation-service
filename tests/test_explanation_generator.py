from app.ml.explanation_generator import ExplanationGenerator


class FakeProduct:
    def __init__(self, description, rating=4.0):
        self.id = 1
        self.name = "Silver Chain"
        self.category = "Jewelry"
        self.brand = None
        self.description = description
        self.tags = []
        self.attributes = {}
        self.review_summary = ""
        self.average_rating = rating


def test_explanation_matches_user_preference():
    product = FakeProduct("Minimal lightweight silver chain")

    reason = ExplanationGenerator().generate(
        product=product,
        user_preferences=["minimal", "lightweight"],
    )

    assert "minimal" in reason
    assert "lightweight" in reason


def test_explanation_uses_rating_when_no_preference_match():
    product = FakeProduct("Luxury diamond ring", rating=4.8)

    reason = ExplanationGenerator().generate(
        product=product,
        user_preferences=["minimal"],
    )

    assert "Highly rated" in reason