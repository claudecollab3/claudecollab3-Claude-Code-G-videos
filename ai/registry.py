"""Builds the default AI ensemble: every model, equal starting weight."""

from ai.ensemble import EnsembleEngine
from ai.models.bayesian import BayesianModel
from ai.models.gbm import XGBoostModel
from ai.models.lightgbm_model import LightGBMModel
from ai.models.neural import NeuralNetworkModel
from ai.models.rl_agent import RLAgentModel
from ai.models.timeseries import TimeSeriesMomentumModel


def build_default_ensemble(weights: dict[str, float] | None = None) -> EnsembleEngine:
    models = [
        TimeSeriesMomentumModel(),
        XGBoostModel(),
        LightGBMModel(),
        BayesianModel(),
        NeuralNetworkModel(),
        RLAgentModel(),
    ]
    return EnsembleEngine(models, weights)
