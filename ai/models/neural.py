"""Feed-forward neural network directional classifier.

This is a lightweight stand-in for the "Deep Learning"/LSTM/Transformer
models the spec calls for: training a real sequence model (LSTM/
Transformer) needs PyTorch or TensorFlow, both several-hundred-megabyte
dependencies that aren't practical to install in this environment. It sits
behind the exact same `Model` interface, so swapping in a real PyTorch-based
sequence model later is a drop-in replacement, not a redesign.
"""

from typing import Any

from sklearn.neural_network import MLPClassifier

from ai.models.sklearn_base import SklearnCompatibleModel


class NeuralNetworkModel(SklearnCompatibleModel):
    name = "neural_network"

    def __init__(self, **kwargs: Any):
        defaults: dict[str, Any] = {"hidden_layer_sizes": (16, 8), "max_iter": 500}
        defaults.update(kwargs)
        super().__init__(MLPClassifier(**defaults))
