import React, { useEffect, useState } from "react";
import { apiJson } from "../api";

interface BrokerCredential {
  id: string;
  broker_type: string;
  broker_name: string;
  server: string;
  login: string;
  is_active: boolean;
  created_at: string;
}

interface AccountInfo {
  login: string;
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  currency: string;
  leverage: number;
  server: string;
}

export default function OverviewPage() {
  const [credentials, setCredentials] = useState<BrokerCredential[]>([]);
  const [accountInfo, setAccountInfo] = useState<Record<string, AccountInfo>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiJson<BrokerCredential[]>("/broker/credentials")
      .then(setCredentials)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function checkAccount(id: string) {
    try {
      const info = await apiJson<AccountInfo>(`/broker/credentials/${id}/connect`, { method: "POST" });
      setAccountInfo((prev) => ({ ...prev, [id]: info }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect");
    }
  }

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>Overview</h2>
      <p className="hint">
        No live trade ledger exists yet in this build — balance/equity below come from a real broker
        connection check, and profit/loss history comes from the Backtesting tab, not a fabricated
        live P&amp;L feed.
      </p>
      {error && <p className="error">{error}</p>}
      {credentials.length === 0 && (
        <p className="hint">No broker accounts connected yet. Add one in the Broker tab.</p>
      )}
      <div className="card-grid">
        {credentials.map((cred) => {
          const info = accountInfo[cred.id];
          return (
            <div key={cred.id} className="card">
              <h3>
                {cred.broker_name} <span className="muted">({cred.broker_type})</span>
              </h3>
              <p className="muted">{cred.server || "no server configured"}</p>
              {info ? (
                <div className="stat-row">
                  <div>
                    <span className="stat-label">Balance</span>
                    <span className="stat-value">
                      {info.balance.toFixed(2)} {info.currency}
                    </span>
                  </div>
                  <div>
                    <span className="stat-label">Equity</span>
                    <span className="stat-value">
                      {info.equity.toFixed(2)} {info.currency}
                    </span>
                  </div>
                  <div>
                    <span className="stat-label">Leverage</span>
                    <span className="stat-value">1:{info.leverage}</span>
                  </div>
                </div>
              ) : (
                <button type="button" className="btn-secondary" onClick={() => checkAccount(cred.id)}>
                  Check balance
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
