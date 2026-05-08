"""

Takes the top-N candidates from ContentBasedRecommender and asks GPT-4 to
re-rank them based on the user's profile and recent feedback history.

Design decisions:
- Falls back to original ML ranking if OpenAI fails or times out.
- Only called when the user has >= MIN_FEEDBACK_COUNT interactions.
- Returns re-ranked product IDs paired with LLM-generated reasons.
- Uses structured JSON output from GPT-4 for reliable parsing.
"""

import json
from openai import OpenAI, OpenAIError
from app.core.logging import get_logger
from app.config import settings
logger = get_logger(__name__)

MIN_FEEDBACK_COUNT = 3  # minimum interactions before LLM re-ranking kicks in

class LLMReranker:
    """
    Re-ranks a list of candidate product IDs using GPT-4.

    Args:
        candidates:   list of Product ORM objects (the ML shortlist)
        user:         User ORM object (age, gender, interests)
        feedback:     list of dicts — [{"product_name": ..., "action": ...}]

    Returns:
        list of dicts: [{"product_id": int, "reason": str}, ...]
        ordered by LLM preference, or None if re-ranking failed/skipped.
    """

    def rerank(
        self,
        candidates: list,
        user,
        feedback: list[dict],
        user_context: list[str] | None = None,
    ) -> list[dict] | None:

        # Only re-rank when user has enough history for the LLM to reason about
        if len(feedback) < MIN_FEEDBACK_COUNT:
            logger.info(
                f"Skipping LLM re-rank — only {len(feedback)} feedback items "
                f"(minimum {MIN_FEEDBACK_COUNT} required)"
            )
            return None

        if not settings.openai_api_key:
            logger.info("Skipping LLM re-rank — OPENAI_API_KEY is not set")
            return None

       
        prompt = self._build_prompt(
                    candidates=candidates,
                    user=user,
                    feedback=feedback,
                    user_context=user_context,
                )

        try:
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a product recommendation engine. "
                            "Re-rank the given product candidates based on the user profile "
                            "and their interaction history. "
                            "Respond ONLY with a valid JSON array — no explanation, no markdown. "
                            "Each element must have: product_id (int) and reason (string, max 20 words)."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=600,
                timeout=30,
            )


            raw = response.choices[0].message.content.strip()
            reranked = self._parse_response(raw, candidates)
            logger.info(f"LLM re-ranking succeeded — {len(reranked)} items returned")
            return reranked

        except OpenAIError as e:
            logger.warning(f"OpenAI error during re-ranking, falling back to ML order: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error during LLM re-ranking, falling back: {e}")
            return None

    def _build_prompt(self, candidates: list, user, feedback: list[dict], user_context: list[str] | None = None,) -> str:
        prompt = "User profile:\n"
        prompt += f"{user}\n\n"

        prompt += "Recent feedback:\n"
        for item in feedback:
            prompt += f"- {item}\n"

        if user_context:
            prompt += "\nRelevant retrieved user history:\n"
            for context in user_context:
                prompt += f"- {context}\n"

        prompt += "\nCandidate products:\n"
        for product in candidates:
            prompt += (
                f"- Product ID: {product.id}, "
                f"Name: {product.name}, "
                f"Category: {getattr(product, 'category', None)}, "
                f"Description: {getattr(product, 'description', None)}\n"
            )

        return prompt

    def _parse_response(self, raw: str, candidates: list) -> list[dict]:
        """
        Parse GPT-4's JSON response. Falls back to ML order if parsing fails
        or if the LLM hallucinates product IDs not in the candidate list.
        """
        valid_ids = {p.id for p in candidates}

        try:
            # Strip any accidental markdown fences
            clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            parsed = json.loads(clean)

            if not isinstance(parsed, list):
                raise ValueError("Expected a JSON array")

            result = []
            seen = set()
            for item in parsed:
                pid = item.get("product_id")
                reason = item.get("reason", "Recommended for you")

                # Only include valid candidate IDs — ignore hallucinated ones
                if pid in valid_ids and pid not in seen:
                    result.append({"product_id": pid, "reason": reason})
                    seen.add(pid)

            # If LLM dropped some candidates, append the missing ones at the end
            for p in candidates:
                if p.id not in seen:
                    result.append({"product_id": p.id, "reason": "Recommended for you"})

            return result

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response: {e}. Raw: {raw[:200]}")
            # Fall back: return candidates in original ML order with no reasons
            return [{"product_id": p.id, "reason": "Recommended for you"} for p in candidates]
