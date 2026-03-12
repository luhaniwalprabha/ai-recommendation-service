"""
Tests for app/ml/llm_reranker.py

OpenAI is fully mocked — no API calls are made during tests.
Covers: re-ranking, fallback on error, feedback threshold, response parsing.
"""

import json
from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_products(ids_and_names: list[tuple]) -> list:
    """Create mock Product objects."""
    products = []
    for pid, name, category, price in ids_and_names:
        p = MagicMock()
        p.id = pid
        p.name = name
        p.category = category
        p.price = price
        products.append(p)
    return products


def make_user(interests=None):
    user = MagicMock()
    user.age = 28
    user.gender = "female"
    user.interests = interests or ["sports", "electronics"]
    return user


def make_feedback(n: int) -> list[dict]:
    return [
        {"product_id": i, "product_name": f"Product {i}",
         "category": "sports", "price": 999, "action": "like"}
        for i in range(n)
    ]


def mock_openai_response(payload: list) -> MagicMock:
    """Build a mock that looks like an OpenAI chat completion response."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(payload)
    return mock_response


# ---------------------------------------------------------------------------
# Threshold tests
# ---------------------------------------------------------------------------

def test_skips_reranking_below_feedback_threshold():
    """LLM is NOT called when user has fewer than MIN_FEEDBACK_COUNT interactions."""
    from app.ml.llm_reranker import LLMReranker, MIN_FEEDBACK_COUNT

    products = make_products([(1, "Shoes", "sports", 999)])
    feedback = make_feedback(MIN_FEEDBACK_COUNT - 1)  # one short

    with patch("app.ml.llm_reranker.openai.chat.completions.create") as mock_call:
        result = LLMReranker().rerank(products, make_user(), feedback)

    mock_call.assert_not_called()
    assert result is None


def test_calls_llm_at_feedback_threshold():
    """LLM IS called when user has exactly MIN_FEEDBACK_COUNT interactions."""
    from app.ml.llm_reranker import LLMReranker, MIN_FEEDBACK_COUNT

    products = make_products([(1, "Shoes", "sports", 999)])
    feedback = make_feedback(MIN_FEEDBACK_COUNT)

    llm_payload = [{"product_id": 1, "reason": "Matches your sports interest"}]

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=mock_openai_response(llm_payload)):
        result = LLMReranker().rerank(products, make_user(), feedback)

    assert result is not None
    assert result[0]["product_id"] == 1


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_rerank_returns_llm_order(sample_feedback_count=5):
    """LLM result is returned in the order GPT-4 specifies."""
    from app.ml.llm_reranker import LLMReranker

    products = make_products([
        (1, "Running Shoes", "sports", 2999),
        (2, "Laptop", "electronics", 65000),
        (3, "T-Shirt", "fashion", 599),
    ])
    feedback = make_feedback(5)

    # LLM reverses the order
    llm_payload = [
        {"product_id": 3, "reason": "Budget-friendly fashion pick"},
        {"product_id": 1, "reason": "Great for your active lifestyle"},
        {"product_id": 2, "reason": "Top electronics choice"},
    ]

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=mock_openai_response(llm_payload)):
        result = LLMReranker().rerank(products, make_user(), feedback)

    assert [r["product_id"] for r in result] == [3, 1, 2]


def test_rerank_includes_reasons():
    """Each re-ranked item has a non-empty reason string."""
    from app.ml.llm_reranker import LLMReranker

    products = make_products([(1, "Shoes", "sports", 999)])
    feedback = make_feedback(5)
    llm_payload = [{"product_id": 1, "reason": "Perfect for your fitness goals"}]

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=mock_openai_response(llm_payload)):
        result = LLMReranker().rerank(products, make_user(), feedback)

    assert result[0]["reason"] == "Perfect for your fitness goals"


# ---------------------------------------------------------------------------
# Fallback behaviour
# ---------------------------------------------------------------------------

def test_falls_back_on_openai_error():
    """Returns None (triggers ML fallback) when OpenAI raises an exception."""
    from app.ml.llm_reranker import LLMReranker
    import openai as openai_module

    products = make_products([(1, "Shoes", "sports", 999)])
    feedback = make_feedback(5)

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               side_effect=openai_module.OpenAIError("API unavailable")):
        result = LLMReranker().rerank(products, make_user(), feedback)

    assert result is None


def test_falls_back_on_timeout():
    """Returns None when OpenAI call times out."""
    from app.ml.llm_reranker import LLMReranker

    products = make_products([(1, "Shoes", "sports", 999)])
    feedback = make_feedback(5)

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               side_effect=Exception("timeout")):
        result = LLMReranker().rerank(products, make_user(), feedback)

    assert result is None


# ---------------------------------------------------------------------------
# Response parsing robustness
# ---------------------------------------------------------------------------

def test_ignores_hallucinated_product_ids():
    """LLM-invented product IDs not in the candidate list are dropped."""
    from app.ml.llm_reranker import LLMReranker

    products = make_products([(1, "Shoes", "sports", 999), (2, "Laptop", "electronics", 65000)])
    feedback = make_feedback(5)

    # LLM returns a real ID + a hallucinated one (999)
    llm_payload = [
        {"product_id": 1, "reason": "Good fit"},
        {"product_id": 999, "reason": "Hallucinated product"},
    ]

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=mock_openai_response(llm_payload)):
        result = LLMReranker().rerank(products, make_user(), feedback)

    result_ids = [r["product_id"] for r in result]
    assert 999 not in result_ids
    assert 1 in result_ids
    # product 2 was dropped by LLM but should be appended at end
    assert 2 in result_ids


def test_handles_malformed_json_gracefully():
    """Falls back to ML order when GPT-4 returns unparseable content."""
    from app.ml.llm_reranker import LLMReranker

    products = make_products([
        (1, "Shoes", "sports", 999),
        (2, "Laptop", "electronics", 65000),
    ])
    feedback = make_feedback(5)

    bad_response = MagicMock()
    bad_response.choices[0].message.content = "Sorry, I cannot help with that."

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=bad_response):
        result = LLMReranker().rerank(products, make_user(), feedback)

    # Should fall back to original order with default reasons
    assert result is not None
    assert len(result) == 2
    assert all(r["reason"] == "Recommended for you" for r in result)


def test_handles_markdown_wrapped_json():
    """GPT-4 sometimes wraps JSON in markdown fences — parser should strip them."""
    from app.ml.llm_reranker import LLMReranker

    products = make_products([(1, "Shoes", "sports", 999)])
    feedback = make_feedback(5)

    fenced_response = MagicMock()
    fenced_response.choices[0].message.content = (
        "```json\n[{\"product_id\": 1, \"reason\": \"Great choice\"}]\n```"
    )

    with patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=fenced_response):
        result = LLMReranker().rerank(products, make_user(), feedback)

    assert result[0]["product_id"] == 1
    assert result[0]["reason"] == "Great choice"


# ---------------------------------------------------------------------------
# Integration: recommendation_service uses LLM when available
# ---------------------------------------------------------------------------

def test_recommendation_service_uses_llm_when_feedback_sufficient(db, sample_user, sample_products, sample_feedback):
    """Full service.generate() triggers LLM re-ranking when feedback threshold is met."""
    from app.repositories.recommendation_repository import RecommendationRepository
    from app.repositories.product_repository import ProductRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.feedback_repository import FeedbackRepository
    from app.services.recommendation_service import RecommendationService
    from app.models.recommendation import Recommendation

    # Add more feedback to pass the threshold
    from app.models.feedback import Feedback
    for product in sample_products[3:]:
        db.add(Feedback(user_id=sample_user.id, product_id=product.id, action="like"))
    db.commit()

    rec_repo = RecommendationRepository(db)
    product_repo = ProductRepository(db)
    user_repo = UserRepository(db)
    feedback_repo = FeedbackRepository(db)
    service = RecommendationService(rec_repo, product_repo, user_repo, feedback_repo)

    mock_recommender = MagicMock()
    mock_recommender.recommend_similar.return_value = [p.id for p in sample_products]

    llm_payload = [
        {"product_id": p.id, "reason": f"Great {p.category} pick"}
        for p in sample_products[:5]
    ]

    with patch("app.services.recommendation_service.acquire_lock", return_value=True), \
         patch("app.services.recommendation_service.ContentBasedRecommender", return_value=mock_recommender), \
         patch("app.ml.llm_reranker.openai.chat.completions.create",
               return_value=mock_openai_response(llm_payload)), \
         patch("app.services.recommendation_service.cache_set"), \
         patch("app.services.recommendation_service.cache_delete"):

        service.generate(sample_user.id)

    saved = db.query(Recommendation).filter_by(user_id=sample_user.id).first()
    assert saved is not None


def test_recommendation_service_falls_back_to_ml_when_llm_fails(db, sample_user, sample_products):
    """service.generate() uses ML order when OpenAI fails."""
    from app.repositories.recommendation_repository import RecommendationRepository
    from app.repositories.product_repository import ProductRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.feedback_repository import FeedbackRepository
    from app.services.recommendation_service import RecommendationService
    from app.models.recommendation import Recommendation
    from app.models.feedback import Feedback
    import openai as openai_module

    for product in sample_products:
        db.add(Feedback(user_id=sample_user.id, product_id=product.id, action="like"))
    db.commit()

    service = RecommendationService(
        RecommendationRepository(db),
        ProductRepository(db),
        UserRepository(db),
        FeedbackRepository(db),
    )

    mock_recommender = MagicMock()
    mock_recommender.recommend_similar.return_value = [p.id for p in sample_products]

    with patch("app.services.recommendation_service.acquire_lock", return_value=True), \
         patch("app.services.recommendation_service.ContentBasedRecommender", return_value=mock_recommender), \
         patch("app.ml.llm_reranker.openai.chat.completions.create",
               side_effect=openai_module.OpenAIError("down")), \
         patch("app.services.recommendation_service.cache_set"), \
         patch("app.services.recommendation_service.cache_delete"):

        service.generate(sample_user.id)

    # Should still save — using ML order as fallback
    saved = db.query(Recommendation).filter_by(user_id=sample_user.id).first()
    assert saved is not None