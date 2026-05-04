from app.rag.product_document_builder import ProductDocumentBuilder


class FakeProduct:
    id = 1
    name = "Gold Necklace"
    category = "Jewelry"
    brand = "Melorra"
    price = 1200
    description = "Lightweight gold necklace for festive occasions"
    attributes = {"material": "gold", "style": "minimal"}
    tags = ["festive", "wedding"]
    review_summary = "Customers liked the lightweight design"
    average_rating = 4.5


def test_product_document_builder():
    product = FakeProduct()
    doc = ProductDocumentBuilder().build(product)

    assert "Product ID: 1" in doc
    assert "Gold Necklace" in doc
    assert "Lightweight gold necklace" in doc
    assert "festive" in doc