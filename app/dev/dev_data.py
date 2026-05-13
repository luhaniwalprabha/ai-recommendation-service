class DevProduct:
    def __init__(
        self,
        id,
        name,
        category,
        price,
        brand,
        description,
        tags,
        attributes,
        review_summary,
        average_rating,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.brand = brand
        self.description = description
        self.tags = tags
        self.attributes = attributes
        self.review_summary = review_summary
        self.average_rating = average_rating


def get_dev_products():
    return [
        DevProduct(
            id=1,
            name="Gold Necklace",
            category="Jewelry",
            price=1000,
            brand="BrandA",
            description="Lightweight festive gold necklace",
            tags=["gold", "festive"],
            attributes={"style": "lightweight"},
            review_summary="Loved for daily wear",
            average_rating=4.5,
        ),
        DevProduct(
            id=2,
            name="Silver Chain",
            category="Jewelry",
            price=500,
            brand="BrandB",
            description="Minimal everyday silver chain",
            tags=["silver", "minimal"],
            attributes={"style": "minimal"},
            review_summary="Simple and elegant",
            average_rating=4.2,
        ),
        DevProduct(
            id=3,
            name="Diamond Ring",
            category="Jewelry",
            price=5000,
            brand="BrandC",
            description="Luxury diamond engagement ring",
            tags=["diamond", "luxury"],
            attributes={"style": "premium"},
            review_summary="Perfect for special occasions",
            average_rating=4.8,
        ),
    ]


def get_dev_user_product_ids():
    return [1]


def get_dev_user(user_id: int):
    return {
        "id": user_id,
        "name": "Test User",
        "preferences": ["minimal", "lightweight"],
    }


def get_dev_feedback(user_id: int):
    return [
        {
            "user_id": user_id,
            "action": "clicked",
            "product_name": "Gold Necklace",
            "category": "Jewelry",
        },
        {
            "user_id": user_id,
            "action": "liked",
            "product_name": "Minimal Ring",
            "category": "Jewelry",
        },
        {
            "user_id": user_id,
            "action": "viewed",
            "product_name": "Silver Chain",
            "category": "Jewelry",
        },
    ]