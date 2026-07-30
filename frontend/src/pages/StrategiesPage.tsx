import React, { useEffect, useState } from "react";
import { apiJson } from "../api";

interface StrategyInfo {
  name: string;
  enabled: boolean;
}

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiJson<StrategyInfo[]>("/strategies")
      .then(setStrategies)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function toggle(name: string, enabled: boolean) {
    try {
      await apiJson(`/strategies/${name}`, { method: "PATCH", body: JSON.stringify({ enabled }) });
      setStrategies((prev) => prev.map((s) => (s.name === name ? { ...s, enabled } : s)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update strategy");
    }
  }

  return (
    <div>
      <h2>Strategies</h2>
      <p className="hint">Enable or disable which strategies contribute signals across every symbol.</p>
      {error && <p className="error">{error}</p>}
      <table className="data-table">
        <thead>
          <tr>
            <th>Strategy</th>
            <th>Enabled</th>
          </tr>
        </thead>
        <tbody>
          {strategies.map((s) => (
            <tr key={s.name}>
              <td>{s.name.replace(/_/g, " ")}</td>
              <td>
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={s.enabled}
                    onChange={(e) => toggle(s.name, e.target.checked)}
                  />
                  <span className="slider" />
                </label>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
