# training/

Offline model training pipelines, built out alongside **Phase 5/6**, kept
strictly isolated from the production inference path.

```
training/
  datasets.py     Load historical MT5/MT4/CSV/tick/OHLC data into training
                  feature sets (reuses ai/features/ so train/infer features
                  never drift apart)
  pipelines/      One training pipeline per model type (gbm, lstm,
                  transformer, bayesian, rl_agent)
  evaluation.py   Out-of-sample validation gate a candidate model must pass
                  before being promoted to production
  registry.py     Versioned model artifacts + metadata (never overwrites a
                  production model in place)
```

Training never runs against the production database/broker connection —
only against historical/exported data — so a bad training run cannot affect
a live account.
