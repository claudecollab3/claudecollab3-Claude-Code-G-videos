import React, { useState } from "react";
import { apiJson } from "../api";

interface RiskDecision {
  approved: boolean;
  reason: string;
  volume: number;
  risk_amount: number;
}

interface SignalResult {
  strategy_name: string;
  symbol: string;
  direction: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  confidence: number;
  reasons: string[];
  risk_decision: RiskDecision;
}

const DEFAULT_ACCOUNT = {
  balance: 10000,
  equity: 10000,
  starting_balance_today: 10000,
  starting_balance_this_week: 10000,
  peak_equity: 10000,
};

export default function SignalsPage() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [results, setResults] = useState<SignalResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  async function evaluate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await apiJson<SignalResult[]>("/signals/evaluate", {
        method: "POST",
        body: JSON.stringify({ symbol, timeframes: ["M15", "H1", "H4"], account: DEFAULT_ACCOUNT }),
      });
      setResults(data);
      setSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to evaluate signals");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Signal Evaluation</h2>
      <p className="hint">
        Uses a placeholder $10,000 account for risk sizing — this checks what the strategy engine and
        risk manager would do, not a live account's real balance.
      </p>
      <form className="inline-form" onSubmit={evaluate}>
        <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="EURUSD" />
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Evaluating..." : "Evaluate"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {searched && results.length === 0 && !loading && (
        <p className="hint">
          No signals fired for {symbol}. Sync market data for this symbol first (Broker tab).
        </p>
      )}
      <div className="card-grid">
        {results.map((r, i) => (
          <div key={i} className="card">
            <h3>
              {r.strategy_name.replace(/_/g, " ")} — {r.direction.toUpperCase()}
            </h3>
            <p className="muted">
              Entry {r.entry_price.toFixed(5)} &middot; SL {r.stop_loss.toFixed(5)} &middot; TP{" "}
              {r.take_profit.toFixed(5)}
            </p>
            <p>
              Confidence: <strong>{r.confidence.toFixed(1)}%</strong>
            </p>
            <p className={r.risk_decision.approved ? "badge-success" : "badge-danger"}>
              {r.risk_decision.approved
                ? `Approved — ${r.risk_decision.volume} lots`
                : `Rejected: ${r.risk_decision.reason}`}
            </p>
            <ul className="reasons">
              {r.reasons.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
