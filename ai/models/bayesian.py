"""Bayesian probabilistic classifier (Gaussian Naive Bayes): a genuinely
Bayesian model (posterior class probability from Gaussian likelihoods and
class priors), distinct from the tree-based and neural models also in this
ensemble."""

from typing import Any

from sklearn.naive_bayes import GaussianNB

from ai.models.sklearn_base import SklearnCompatibleModel


class BayesianModel(SklearnCompatibleModel):
    name = "bayesian"

    def __init__(self, **kwargs: Any):
        super().__init__(GaussianNB(**kwargs))
