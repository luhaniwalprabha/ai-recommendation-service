from app.services.recommendation_service import RecommendationService


class FakeProduct:
    def __init__(self, id, name, category="Jewelry", description=None):
        self.id = id
        self.name = name
        self.category = category
        self.price = 1000
        self.brand = None
        self.description = description
        self.tags = None
        self.attributes = None
        self.review_summary = None
        self.average_rating = None


class FakeRecRepo:
    pass


class FakeProductRepo:
    pass


def test_filter_seen_products():
    service = RecommendationService(
        rec_repo=FakeRecRepo(),
        product_repo=FakeProductRepo(),
    )

    candidate_ids = [1, 2, 3, 4]
    seen_ids = [1, 3]

    result = service._filter_seen_products(candidate_ids, seen_ids)

    assert result == [2, 4]


def test_get_anchor_product_with_recent_product():
    service = RecommendationService(
        rec_repo=FakeRecRepo(),
        product_repo=FakeProductRepo(),
    )

    products = [
        FakeProduct(1, "Gold Necklace"),
        FakeProduct(2, "Silver Ring"),
    ]

    result = service._get_anchor_product([2], products)

    assert result.id == 2


def test_get_anchor_product_fallback():
    service = RecommendationService(
        rec_repo=FakeRecRepo(),
        product_repo=FakeProductRepo(),
    )

    products = [
        FakeProduct(1, "Gold Necklace"),
        FakeProduct(2, "Silver Ring"),
    ]

    result = service._get_anchor_product([], products)

    assert result.id == 1