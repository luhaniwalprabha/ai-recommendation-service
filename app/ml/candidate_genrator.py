from abc import ABC, abstractmethod


class CandidateGenerator(ABC):
    @abstractmethod
    def generate(self, products, anchor_product_id: int, limit: int = 10):
        pass