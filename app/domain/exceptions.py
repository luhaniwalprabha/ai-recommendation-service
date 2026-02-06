class RecommendationError(Exception):
    """Base exception for recommendation domain."""


class InvalidUserError(RecommendationError):
    """Raised when user_id is invalid."""


class RecommendationGenerationError(RecommendationError):
    """Raised when recommendation generation fails."""
