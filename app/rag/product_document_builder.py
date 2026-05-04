class ProductDocumentBuilder:
    def build(self, product):
        parts = [
            f"Product ID: {product.id}",
            f"Name: {product.name}",
            f"Category: {product.category}",
            f"Brand: {getattr(product, 'brand', None)}",
            f"Price: {product.price}",
            f"Description: {getattr(product, 'description', None)}",
            f"Attributes: {getattr(product, 'attributes', None)}",
            f"Tags: {getattr(product, 'tags', None)}",
            f"Review Summary: {getattr(product, 'review_summary', None)}",
            f"Average Rating: {getattr(product, 'average_rating', None)}",
        ]

        return "\n".join([p for p in parts if p and "None" not in p])