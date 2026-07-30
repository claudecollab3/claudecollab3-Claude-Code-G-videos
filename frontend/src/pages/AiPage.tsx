import React, { useState } from "react";
import { apiJson } from "../api";

interface ModelVote {
  model_name: string;
  direction: string;
  probability: number;
  confidence: number;
  fitted: boolean;
}

interface PredictResponse {
  symbol: string;
  direction: string;
  confidence: number;
  votes: ModelVote[];
  weights: Record<string, number>;
}

export default function AiPage() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function predict(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await apiJson<PredictResponse>("/ai/predict", {
        method: "POST",
        body: JSON.stringify({ symbol, timeframes: ["M15", "H1", "H4"], candle_limit: 300 }),
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>AI Ensemble Prediction</h2>
      <p className="hint">
        The neural-net and RL models show as "untrained" until fit on historical data (Phase 6&apos;s
        training pipeline) — the ensemble still works today via the deterministic momentum baseline.
      </p>
      <form className="inline-form" onSubmit={predict}>
        <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="EURUSD" />
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Running..." : "Predict"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && (
        <>
          <div className="card">
            <h3>Ensemble: {result.direction.toUpperCase()}</h3>
            <div className="confidence-bar">
              <div style={{ width: `${result.confidence}%` }} />
            </div>
            <p>{result.confidence.toFixed(1)}% confidence</p>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Direction</th>
                <th>Probability</th>
                <th>Confidence</th>
                <th>Weight</th>
                <th>Trained</th>
              </tr>
            </thead>
            <tbody>
              {result.votes.map((v) => (
                <tr key={v.model_name}>
                  <td>{v.model_name.replace(/_/g, " ")}</td>
                  <td>{v.direction}</td>
                  <td>{(v.probability * 100).toFixed(1)}%</td>
                  <td>{v.confidence.toFixed(1)}%</td>
                  <td>{result.weights[v.model_name]?.toFixed(2) ?? "—"}</td>
                  <td>{v.fitted ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
