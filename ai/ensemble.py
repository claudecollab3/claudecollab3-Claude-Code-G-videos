"""Weighted-consensus ensemble: combines every model's vote into one final
direction + 0-100 confidence score. Weights default to equal and can be
overridden (e.g. once Phase 6 backtesting has measured each model's
historical accuracy). A vote from a not-yet-fitted model is heavily
discounted rather than excluded, so the ensemble degrades gracefully before
any trainable model has been trained."""

from dataclasses import dataclass

from ai.models.base import Model, ModelVote
from strategies.base import Direction

UNFITTED_WEIGHT_DISCOUNT = 0.25


@dataclass
class EnsembleResult:
    direction: Direction
    confidence: float  # 0-100
    votes: list[ModelVote]
    weights: dict[str, float]


class EnsembleEngine:
    def __init__(self, models: list[Model], weights: dict[str, float] | None = None):
        self._models = models
        self._weights = weights or {}

    def _weight_for(self, model_name: str) -> float:
        return self._weights.get(model_name, 1.0)

    def predict(self, features: dict[str, float]) -> EnsembleResult:
        votes = [model.predict(features) for model in self._models]

        weighted_sum = 0.0
        total_weight = 0.0
        weights_used: dict[str, float] = {}

        for vote in votes:
            weight = self._weight_for(vote.model_name)
            if not vote.fitted:
                weight *= UNFITTED_WEIGHT_DISCOUNT
            weights_used[vote.model_name] = weight

            signed_score = (vote.probability - 0.5) * 2  # -1..1
            weighted_sum += signed_score * weight
            total_weight += weight

        consensus = weighted_sum / total_weight if total_weight else 0.0
        direction = Direction.LONG if consensus >= 0 else Direction.SHORT
        confidence = min(100.0, abs(consensus) * 100)

        return EnsembleResult(
            direction=direction, confidence=confidence, votes=votes, weights=weights_used
        )
