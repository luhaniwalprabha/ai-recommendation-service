from app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def get_products(self):
        return self.repo.list_products()
