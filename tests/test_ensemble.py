from ai.ensemble import EnsembleEngine
from ai.models.base import Model, ModelVote
from strategies.base import Direction


class _FixedVoteModel(Model):
    """`probability` is always P(LONG), matching the convention every real
    model follows; `direction` is derived from it, not set independently,
    so a fixture can never construct an internally-contradictory vote
    (e.g. "SHORT" at probability=0.9, which actually means 90% LONG)."""

    def __init__(self, name: str, probability: float, fitted: bool = True):
        self.name = name
        self._probability = probability
        self._fitted = fitted

    def predict(self, features: dict[str, float]) -> ModelVote:
        direction = Direction.LONG if self._probability >= 0.5 else Direction.SHORT
        confidence = abs(self._probability - 0.5) * 200
        return ModelVote(
            model_name=self.name,
            direction=direction,
            probability=self._probability,
            confidence=confidence,
            fitted=self._fitted,
        )


def test_ensemble_unanimous_bullish_high_confidence():
    models = [_FixedVoteModel("a", 0.9), _FixedVoteModel("b", 0.85)]
    result = EnsembleEngine(models).predict({})
    assert result.direction == Direction.LONG
    assert result.confidence > 70


def test_ensemble_split_vote_lowers_confidence():
    models = [_FixedVoteModel("a", 0.9), _FixedVoteModel("b", 0.1)]
    result = EnsembleEngine(models).predict({})
    assert result.confidence < 10  # near-cancelling votes


def test_ensemble_discounts_unfitted_models():
    # Without the unfitted discount these would roughly cancel and even
    # slightly favor SHORT; the discount should flip the outcome to LONG.
    models = [
        _FixedVoteModel("trained", 0.9, fitted=True),
        _FixedVoteModel("untrained", 0.05, fitted=False),
    ]
    result = EnsembleEngine(models).predict({})
    assert result.direction == Direction.LONG


def test_ensemble_respects_custom_weights():
    models = [_FixedVoteModel("a", 0.6), _FixedVoteModel("b", 0.1)]
    # Heavily favor model "a" so it wins despite b's stronger conviction.
    result = EnsembleEngine(models, weights={"a": 10.0, "b": 1.0}).predict({})
    assert result.direction == Direction.LONG


def test_ensemble_returns_all_votes_and_weights():
    models = [_FixedVoteModel("a", 0.7)]
    result = EnsembleEngine(models).predict({})
    assert len(result.votes) == 1
    assert "a" in result.weights
