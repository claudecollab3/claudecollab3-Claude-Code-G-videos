"""LightGBM gradient-boosted-tree directional classifier."""

from typing import Any

from lightgbm import LGBMClassifier

from ai.models.sklearn_base import SklearnCompatibleModel


class LightGBMModel(SklearnCompatibleModel):
    name = "lightgbm"

    def __init__(self, **kwargs: Any):
        super().__init__(LGBMClassifier(n_estimators=100, max_depth=3, verbose=-1, **kwargs))
