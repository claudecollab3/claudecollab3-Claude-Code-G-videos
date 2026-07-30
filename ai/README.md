# ai/

The AI decision engine, news engine, and Decision & Confidence Engine.

## Implemented in Phase 5

```
ai/
  features.py       build_feature_vector(MarketContext) -> fixed-order
                     numeric dict every model reads (EMA spread, RSI, MACD
                     histogram, ADX, ATR%, %B, volume ratio, kill-zone flag)
  models/
    base.py          Model ABC + ModelVote (direction, P(long), confidence, fitted)
    timeseries.py     Deterministic EMA-spread momentum baseline (no training needed)
    sklearn_base.py   Shared fit()/predict() scaffolding for scikit-learn-API models
    gbm.py            XGBoost
    lightgbm_model.py LightGBM
    bayesian.py       Gaussian Naive Bayes (a genuinely Bayesian model)
    neural.py         MLPClassifier — see note below
    rl_agent.py        Epsilon-free contextual-bandit agent with record_outcome()
  ensemble.py        EnsembleEngine: weighted-consensus vote -> direction + 0-100
                     confidence; an unfitted model's vote is discounted, not excluded
  registry.py        build_default_ensemble() — every model, equal starting weight
  decision.py        DecisionEngine: strategy signals + AI ensemble + news policy
                     -> confirmed signals with a pass/fail checklist. A signal the
                     AI disagrees with, or that falls in a news blackout, comes out
                     confidence=0 so RiskManager rejects it the same way it rejects
                     any other low-confidence signal.
  news/
    calendar.py       CalendarEvent, EconomicCalendarProvider (pluggable),
                      StaticCalendarProvider (default: empty), HttpCalendarProvider
                      (generic JSON client — no vendor wired in, see below)
    policy.py         NewsPolicy: Trade / Wait / Reduce risk / Close existing
    factory.py        get_calendar_provider() from settings
```

Exposed via `POST /api/v1/ai/predict` (runs the ensemble, persists an
`AIPrediction` row), `GET /api/v1/news/upcoming` / `POST /api/v1/news/policy`,
and `POST /api/v1/decision/evaluate` (the full strategies -> AI -> news ->
risk pipeline in one call).

### Honest scope notes

- **"Deep Learning"/LSTM/Transformer**: `neural.py` uses scikit-learn's
  `MLPClassifier`, not PyTorch/TensorFlow. A real sequence model needs one of
  those frameworks, each several hundred megabytes — impractical to install
  in this environment. It sits behind the exact same `Model` interface, so
  swapping in a real PyTorch-based LSTM/Transformer is a drop-in replacement,
  not a redesign.
- **"Reinforcement Learning"**: `rl_agent.py` is a simple contextual bandit
  (epsilon-free, incremental action-value averaging via `record_outcome()`),
  not a deep RL agent (PPO/DQN via stable-baselines3), which needs a full
  training environment and GPU-scale compute.
- **Economic calendar**: no vendor is wired in — the spec doesn't name one,
  and fabricating a real provider's URL isn't something to guess at.
  `StaticCalendarProvider` (empty list) is the default until
  `ECONOMIC_CALENDAR_API_KEY` and `ECONOMIC_CALENDAR_BASE_URL` are both set.
- **Model training**: every scikit-learn-style model returns a neutral,
  clearly-marked "unfitted" vote until `.fit()` has been called — a fresh
  deployment has no trained model yet. Phase 6's backtesting/training
  pipeline is what produces one from historical data.
- **Notification dispatch**: `NewsPolicy` decides *what* to say (e.g. "High-
  impact news 'NFP' in 10 minutes") — actually sending that to Telegram/
  Discord/email is `notifications/`, Phase 7.
