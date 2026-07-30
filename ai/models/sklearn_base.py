"""Shared scaffolding for scikit-learn-API-compatible classifiers (gbm,
lightgbm, bayesian, neural). Each predicts P(direction=LONG) from the fixed-
order feature vector. Until `fit()` has been called, `predict()` returns a
neutral, unfitted vote rather than raising — a fresh deployment has no
trained model yet; Phase 6's training pipeline is what produces one."""

from typing import Any

from ai.features import feature_dict_to_vector
from ai.models.base import Model, ModelVote
from strategies.base import Direction


class SklearnCompatibleModel(Model):
    def __init__(self, estimator: Any):
        self._estimator = estimator
        self._fitted = False

    def fit(self, X: list[list[float]], y: list[int]) -> None:
        self._estimator.fit(X, y)
        self._fitted = True

    def predict(self, features: dict[str, float]) -> ModelVote:
        if not self._fitted:
            return ModelVote(
                model_name=self.name,
                direction=Direction.LONG,
                probability=0.5,
                confidence=0.0,
                fitted=False,
            )

        vector = [feature_dict_to_vector(features)]
        probability = float(self._estimator.predict_proba(vector)[0][1])
        direction = Direction.LONG if probability >= 0.5 else Direction.SHORT
        confidence = abs(probability - 0.5) * 200
        return ModelVote(
            model_name=self.name,
            direction=direction,
            probability=probability,
            confidence=confidence,
        )
