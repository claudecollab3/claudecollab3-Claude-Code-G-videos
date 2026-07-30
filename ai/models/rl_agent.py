"""A lightweight contextual-bandit-style reinforcement-learning agent:
learns action values (long/short) per discretized market state from
realized trade outcomes via simple incremental averaging.

This is a genuine (if simple) RL technique — not a deep RL agent (e.g.
PPO/DQN via stable-baselines3), which needs a full training environment and
GPU-scale compute impractical here. It sits behind the same `Model`
interface used for prediction; `record_outcome` is how it actually learns.
"""

from ai.models.base import Model, ModelVote
from strategies.base import Direction


def _discretize(value: float, edges: tuple[float, ...]) -> int:
    for i, edge in enumerate(edges):
        if value <= edge:
            return i
    return len(edges)


class RLAgentModel(Model):
    name = "rl_agent"

    def __init__(self) -> None:
        self._action_values: dict[tuple[int, str], float] = {}
        self._action_counts: dict[tuple[int, str], int] = {}

    def _state(self, features: dict[str, float]) -> int:
        return _discretize(features.get("h1_ema_fast_slow_diff_pct", 0.0), (-1.0, -0.25, 0.25, 1.0))

    def predict(self, features: dict[str, float]) -> ModelVote:
        state = self._state(features)
        long_value = self._action_values.get((state, "long"), 0.0)
        short_value = self._action_values.get((state, "short"), 0.0)

        if long_value == 0.0 and short_value == 0.0:
            return ModelVote(
                model_name=self.name,
                direction=Direction.LONG,
                probability=0.5,
                confidence=0.0,
                fitted=False,
            )

        total = abs(long_value) + abs(short_value)
        probability = 0.5 + (long_value - short_value) / (2 * total) if total else 0.5
        direction = Direction.LONG if probability >= 0.5 else Direction.SHORT
        confidence = min(100.0, abs(probability - 0.5) * 200)
        return ModelVote(
            model_name=self.name,
            direction=direction,
            probability=probability,
            confidence=confidence,
        )

    def record_outcome(
        self, features: dict[str, float], direction: Direction, reward: float
    ) -> None:
        """Incrementally updates the action-value estimate for the state a
        signal was generated in, given the realized trade outcome (e.g. an
        R-multiple, or a simple +1/-1 win/loss)."""
        state = self._state(features)
        key = (state, "long" if direction == Direction.LONG else "short")
        count = self._action_counts.get(key, 0) + 1
        old_value = self._action_values.get(key, 0.0)
        self._action_values[key] = old_value + (reward - old_value) / count
        self._action_counts[key] = count
