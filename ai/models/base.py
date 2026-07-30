"""Common interface every AI model in the ensemble implements."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from strategies.base import Direction


@dataclass
class ModelVote:
    model_name: str
    direction: Direction
    probability: float  # probability of the LONG/bullish class, 0-1
    confidence: float  # 0-100, derived from how far probability is from 0.5
    fitted: bool = True  # False = no trained signal yet; a neutral placeholder vote


class Model(ABC):
    name: str = "base"

    @abstractmethod
    def predict(self, features: dict[str, float]) -> ModelVote:
        raise NotImplementedError
