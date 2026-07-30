"""XGBoost gradient-boosted-tree directional classifier."""

from typing import Any

from xgboost import XGBClassifier

from ai.models.sklearn_base import SklearnCompatibleModel


class XGBoostModel(SklearnCompatibleModel):
    name = "xgboost"

    def __init__(self, **kwargs: Any):
        super().__init__(
            XGBClassifier(n_estimators=100, max_depth=3, eval_metric="logloss", **kwargs)
        )
