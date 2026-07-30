from ai.features import FEATURE_NAMES, feature_dict_to_vector
from ai.models.bayesian import BayesianModel
from ai.models.gbm import XGBoostModel
from ai.models.lightgbm_model import LightGBMModel
from ai.models.neural import NeuralNetworkModel
from ai.models.rl_agent import RLAgentModel
from ai.models.timeseries import TimeSeriesMomentumModel
from strategies.base import Direction

_BULLISH_FEATURES = dict.fromkeys(FEATURE_NAMES, 0.0) | {"h1_ema_fast_slow_diff_pct": 0.8}
_BEARISH_FEATURES = dict.fromkeys(FEATURE_NAMES, 0.0) | {"h1_ema_fast_slow_diff_pct": -0.8}


def _synthetic_training_data(n: int = 200):
    """Features/labels where the sign of h1_ema_fast_slow_diff_pct
    perfectly determines the label, so any reasonable classifier should
    learn it easily."""
    import random

    random.seed(42)
    X, y = [], []
    for _ in range(n):
        spread = random.uniform(-2, 2)
        features = dict.fromkeys(FEATURE_NAMES, 0.0) | {"h1_ema_fast_slow_diff_pct": spread}
        X.append(feature_dict_to_vector(features))
        y.append(1 if spread > 0 else 0)
    return X, y


def test_timeseries_model_bullish_and_bearish():
    model = TimeSeriesMomentumModel()
    bullish_vote = model.predict(_BULLISH_FEATURES)
    bearish_vote = model.predict(_BEARISH_FEATURES)
    assert bullish_vote.direction == Direction.LONG
    assert bearish_vote.direction == Direction.SHORT
    assert bullish_vote.fitted is True


def test_sklearn_models_return_neutral_vote_before_fit():
    for model in (XGBoostModel(), LightGBMModel(), BayesianModel(), NeuralNetworkModel()):
        vote = model.predict(_BULLISH_FEATURES)
        assert vote.fitted is False
        assert vote.confidence == 0.0
        assert vote.probability == 0.5


def test_sklearn_models_learn_a_trivial_pattern_after_fit():
    X, y = _synthetic_training_data()
    for model in (XGBoostModel(), LightGBMModel(), BayesianModel(), NeuralNetworkModel()):
        model.fit(X, y)
        bullish_vote = model.predict(_BULLISH_FEATURES)
        bearish_vote = model.predict(_BEARISH_FEATURES)
        assert bullish_vote.fitted is True
        assert bullish_vote.direction == Direction.LONG, model.name
        assert bearish_vote.direction == Direction.SHORT, model.name


def test_rl_agent_starts_neutral_and_learns_from_outcomes():
    agent = RLAgentModel()
    initial_vote = agent.predict(_BULLISH_FEATURES)
    assert initial_vote.fitted is False

    for _ in range(10):
        agent.record_outcome(_BULLISH_FEATURES, Direction.LONG, reward=1.0)
        agent.record_outcome(_BULLISH_FEATURES, Direction.SHORT, reward=-1.0)

    learned_vote = agent.predict(_BULLISH_FEATURES)
    assert learned_vote.fitted is True
    assert learned_vote.direction == Direction.LONG
