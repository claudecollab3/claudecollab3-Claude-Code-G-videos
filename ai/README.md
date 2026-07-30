# ai/

The AI decision engine. Implemented in **Phase 5**.

Planned structure:

```
ai/
  features/       Feature engineering shared across all models (indicators,
                  SMC/ICT features, session/time features, news features)
  models/
    gbm.py        XGBoost / LightGBM directional classifiers
    lstm.py       LSTM time-series forecaster
    transformer.py Transformer-based sequence model
    bayesian.py   Bayesian probabilistic model
    rl_agent.py   Reinforcement-learning execution/sizing agent
  ensemble.py     Weighted-consensus voting across all models -> confidence score
  inference.py    Low-latency ONNX Runtime inference wrapper for production
```

Each model exposes a common interface (`predict(features) -> ModelVote`) so
the ensemble can combine arbitrary models without special-casing any one of
them. Model weights are derived from rolling out-of-sample performance, not
hardcoded forever, and are stored/versioned in the database (`ai_predictions`,
`model_registry` tables — Phase 2 schema, Phase 5 usage).
