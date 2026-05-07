
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
        
    ):
        self.rec_repo = rec_repo
        self.product_repo = product_repo
        self.user_repo = user_repo
        self.feedback_repo = feedback_repo
        self.product_vector_index = ProductVectorIndex()

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

        stale = self.rec_repo.latest_items(user_id)
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

    def generate(self, user_id: int):
        logger.info(f"Generating recommendations for user_id={user_id}")

        lock_key = f"lock:recs:{user_id}"

        if not acquire_lock(lock_key, ttl=120):
            logger.info(f"Skipping generation for user_id={user_id} - lock held")
            return

        try:
           
            products = self.product_repo.list_products(limit=200)

            if not products:
                logger.warning(f"No products found - skipping for user_id={user_id}")
                return


            user_product_ids = self.rec_repo.get_user_recent_products(user_id)

            anchor_product = self._get_anchor_product(user_product_ids, products)

            candidate_ids = self._generate_candidates(products, anchor_product)
            logger.info(f"Raw candidate IDs: {candidate_ids}")
        
            filtered_ids = self._filter_seen_products(candidate_ids, user_product_ids)
            logger.info(f"Filtered candidate IDs: {filtered_ids}")

            candidate_products = self._map_products(filtered_ids, products)
            logger.info(
                f"Candidate products: {[p.id for p in candidate_products]}"
            )

            self._evaluate_candidates(candidate_products, anchor_product)

            reranked = False
            final_items: list[dict] = []

            if self.user_repo and self.feedback_repo:
                user = self.user_repo.get(user_id)
                raw_feedback = self.feedback_repo.get_recent_with_details(user_id, limit=20)

                reranker = LLMReranker()
                logger.info(f"LLM received {len(candidate_products)} candidates")

                llm_result = reranker.rerank(
                    candidates=candidate_products,
                    user=user,
                    feedback=raw_feedback,
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
                ]
                logger.info(f"Using ML order for user_id={user_id} (no LLM re-ranking)")

            # ----------------------------------------------------------------
            # Step 3: Persist to DB and cache
            # ----------------------------------------------------------------
            item_ids = [item["product_id"] for item in final_items]
            self.rec_repo.save(user_id, item_ids)

            payload = {
                "items": final_items,   # list of {"product_id": int, "reason": str|None}
                "reranked": reranked,
                "generated_at": time.time(),
            }

            cache_key = f"recommendations:{user_id}"
            cache_set(cache_key, payload, ttl=3600)

            logger.info(
                f"Saved recommendations for user_id={user_id} "
                f"(reranked={reranked}, count={len(final_items)})"
            )

        finally:
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