"""Simple statistical time-series momentum model: direction/confidence
derived directly from the EMA fast/slow spread already in the feature
vector. Needs no training data, so the ensemble has a sane baseline even
before any trainable model has been fit."""

from ai.models.base import Model, ModelVote
from strategies.base import Direction


class TimeSeriesMomentumModel(Model):
    name = "time_series_momentum"

    def predict(self, features: dict[str, float]) -> ModelVote:
        spread_pct = features.get("h1_ema_fast_slow_diff_pct", 0.0)
        # Squash the EMA spread (%) into a 0-1 probability around 0.5.
        probability = 0.5 + max(-0.5, min(0.5, spread_pct / 2))
        direction = Direction.LONG if probability >= 0.5 else Direction.SHORT
        confidence = abs(probability - 0.5) * 200
        return ModelVote(
            model_name=self.name,
            direction=direction,
            probability=probability,
            confidence=confidence,
        )
