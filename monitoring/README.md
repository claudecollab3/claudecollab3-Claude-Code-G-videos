# monitoring/

Health checks, metrics, and alerting, built out in **Phase 8** (with basic
health endpoints already present in `backend/app/api/v1/health.py` from
Phase 1).

```
monitoring/
  metrics.py      Execution latency, slippage, model drift, signal throughput
  healthchecks.py DB/Redis/broker connectivity probes
  alerting.py     Threshold-based ops alerts (distinct from user-facing
                  notifications/ — this is for system operators)
```
