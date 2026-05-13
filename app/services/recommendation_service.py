
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.cache.redis_client import get as cache_get, set as cache_set, delete as cache_delete, acquire_lock
from app.core.logging import get_logger
from app.schemas.recommendation import RecommendationItem
from app.config import settings
from app.rag.product_index_builder import ProductIndexBuilder
from app.ml.vector_candidate_generator import VectorCandidateGenerator
from app.ml.llm_reranker import LLMReranker
from app.ml.tfidf_candidate_generator import TfidfCandidateGenerator
from app.rag.product_vector_index import ProductVectorIndex
from app.rag.user_vector_index import UserVectorIndex
from app.ml.hybrid_ranker import HybridRanker
from app.dev.dev_data import (
    get_dev_products,
    get_dev_user_product_ids,
    get_dev_user,
    get_dev_feedback,
)
import time

logger = get_logger(__name__)

TOP_CANDIDATES = 10
FINAL_COUNT = 5


class RecommendationService:
    def __init__(
        self,
        rec_repo: RecommendationRepository,
        product_repo: ProductRepository,
        user_repo: UserRepository | None = None,
        feedback_repo: FeedbackRepository | None = None,
        debug: bool = False,
        use_dev_data: bool = False,
    ):
        self.rec_repo = rec_repo
        self.product_repo = product_repo
        self.user_repo = user_repo
        self.feedback_repo = feedback_repo
        self.product_vector_index = ProductVectorIndex()
        self.user_vector_index = UserVectorIndex()
        self.debug = debug
        self.use_dev_data = use_dev_data

    def get(self, user_id: int):
        """
        Returns (items, should_refresh) where items is a list of dicts:
        [{"product_id": int, "reason": str | None}, ...]
        """
        cache_key = f"recommendations:{user_id}"
        cached = cache_get(cache_key)

        if cached and isinstance(cached, dict) and "items" in cached:
            age = time.time() - cached["generated_at"]
            should_refresh = age > settings.recommendation_soft_ttl_seconds
            return cached["items"], should_refresh

        stale = []
        if stale:
            return stale, True

        return [], True

    def _get_anchor_product(self, user_product_ids, products):
        anchor_product = None

        if user_product_ids:
            anchor_id = user_product_ids[0]
            anchor_product = next((p for p in products if p.id == anchor_id), None)

        if anchor_product is None:
            anchor_product = products[0]

        return anchor_product

    
    def _generate_candidates(self, products, anchor_product):
        try:
            vector_store = self.product_vector_index.build_once(products)

            candidate_generator = VectorCandidateGenerator(
                vector_store=vector_store,
            )

            candidate_ids = candidate_generator.generate(
                products=products,
                anchor_product_id=anchor_product.id,
                limit=TOP_CANDIDATES,
            )
            
            if candidate_ids:
                return candidate_ids

        except Exception as e:
            logger.exception(f"Vector candidate generation failed: {e}")

        fallback_generator = TfidfCandidateGenerator()

        return fallback_generator.generate(
            products=products,
            anchor_product_id=anchor_product.id,
            limit=TOP_CANDIDATES,
        )


    def _filter_seen_products(self, candidate_ids, seen_ids):
        seen = set(seen_ids)
        filtered_ids = [pid for pid in candidate_ids if pid not in seen]

        if not filtered_ids:
            return candidate_ids

        return filtered_ids


    def _map_products(self, product_ids, products):
        product_map = {p.id: p for p in products}
        return [product_map[pid] for pid in product_ids if pid in product_map]


    def _evaluate_candidates(self, candidate_products, anchor_product):
        if not anchor_product:
            return

        logger.info(f"Anchor product: {anchor_product.id}")

        for p in candidate_products[:5]:
            logger.info(
                f"Eval → Anchor {anchor_product.id} vs Candidate {p.id}"
            )


    def _get_user_context(self, user_id, interactions, anchor_product):
        vector_store = self.user_vector_index.build_once(interactions)

        query = f"{anchor_product.name} {anchor_product.category}"

        results = vector_store.search_by_embedding(
            query_embedding=self.user_vector_index.embedding_service.embed_text(query),
            top_k=5,
        )

        context = []

        for r in results:
            context.append(r["text"])

        return context


    def generate(self, user_id: int):
        logger.info(f"Generating recommendations for user_id={user_id}")

        lock_key = f"lock:recs:{user_id}"

        if not self.use_dev_data:
            if not acquire_lock(lock_key, ttl=120):
                logger.info(f"Skipping generation for user_id={user_id} - lock held")
                return

        try:
           
            # products = self.product_repo.list_products(limit=200)
            if self.use_dev_data:
                products = get_dev_products()
            else:
                products = self.product_repo.list_products(limit=200)

            if not products:
                logger.warning(f"No products found - skipping for user_id={user_id}")
                return


            if self.use_dev_data:
                user_product_ids = get_dev_user_product_ids()
            else:
                user_product_ids = self.rec_repo.get_user_recent_products(user_id)

            anchor_product = self._get_anchor_product(user_product_ids, products)

            candidate_ids = self._generate_candidates(products, anchor_product)
            logger.info(f"Raw candidate IDs: {candidate_ids}")
        
            filtered_ids = self._filter_seen_products(candidate_ids, user_product_ids)
            logger.info(f"Filtered candidate IDs: {filtered_ids}")

            candidate_products = self._map_products(filtered_ids, products)
            user_preferences = ["minimal", "lightweight"]

            hybrid_ranker = HybridRanker()

            candidate_products = hybrid_ranker.rank(
                products=candidate_products,
                user_context=[],
                user_preferences=user_preferences,
                limit=TOP_CANDIDATES,
            )

            logger.info(
                f"Hybrid ranked candidate products: {[p.id for p in candidate_products]}"
            )

            self._evaluate_candidates(candidate_products, anchor_product)

            reranked = False
            final_items: list[dict] = []

            if self.use_dev_data:
                user = get_dev_user(user_id)
                raw_feedback = get_dev_feedback(user_id)
            else:
                user = self.user_repo.get(user_id)
                raw_feedback = self.feedback_repo.get_recent_with_details(user_id, limit=20)

            reranker = LLMReranker()
            logger.info(f"LLM received {len(candidate_products)} candidates")

            user_context = self._get_user_context(
                user_id=user_id,
                interactions=raw_feedback,
                anchor_product=anchor_product,
            )


            llm_result = reranker.rerank(
                candidates=candidate_products,
                user=user,
                feedback=raw_feedback,
                user_context=user_context,
            )

            if llm_result:
                final_items = llm_result[:FINAL_COUNT]
                reranked = True
                logger.info(f"LLM re-ranking applied for user_id={user_id}")
                logger.info(f"LLM returned {len(llm_result)} items")

            # Fall back to ML order if LLM skipped or failed
            if not final_items:
                final_items = [
                    {
                        "product_id": p.id,
                        "reason": None,
                        "source": "vector" if reranked else "ml",
                    }
                    for p in candidate_products[:FINAL_COUNT]
                ]
                logger.info(f"Using ML order for user_id={user_id} (no LLM re-ranking)")

        
            item_ids = [item["product_id"] for item in final_items]
            if not self.use_dev_data:
                self.rec_repo.save(user_id, item_ids)

            payload = {
                "items": final_items,   # list of {"product_id": int, "reason": str|None}
                "reranked": reranked,
                "generated_at": time.time(),
            }

            cache_key = f"recommendations:{user_id}"
            if not self.use_dev_data:
                cache_set(cache_key, payload, ttl=3600)

            logger.info(
                f"Saved recommendations for user_id={user_id} "
                f"(reranked={reranked}, count={len(final_items)})"
            )

        finally:
            if not self.use_dev_data:
                cache_delete(lock_key)

    def _normalize_items(self, items) -> list[RecommendationItem]:
        normalized: list[RecommendationItem] = []
        for item in items:
            if isinstance(item, int):
                normalized.append(RecommendationItem(product_id=item))
            elif isinstance(item, dict):
                normalized.append(RecommendationItem(
                    product_id=item["product_id"],
                    reason=item.get("reason"),
                ))
        return normalized