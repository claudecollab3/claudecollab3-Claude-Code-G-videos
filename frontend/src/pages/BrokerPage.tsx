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
  balance: number;
  currency: string;
}

export default function BrokerPage() {
  const [credentials, setCredentials] = useState<BrokerCredential[]>([]);
  const [brokerType, setBrokerType] = useState("paper");
  const [brokerName, setBrokerName] = useState("");
  const [server, setServer] = useState("");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  function load() {
    apiJson<BrokerCredential[]>("/broker/credentials")
      .then(setCredentials)
      .catch((err: Error) => setError(err.message));
  }

  useEffect(load, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiJson("/broker/credentials", {
        method: "POST",
        body: JSON.stringify({
          broker_type: brokerType,
          broker_name: brokerName,
          server,
          login,
          password,
        }),
      });
      setBrokerName("");
      setServer("");
      setLogin("");
      setPassword("");
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create credential");
    }
  }

  async function remove(id: string) {
    try {
      await apiJson(`/broker/credentials/${id}`, { method: "DELETE" });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete credential");
    }
  }

  async function testConnect(id: string) {
    setError(null);
    try {
      const info = await apiJson<AccountInfo>(`/broker/credentials/${id}/connect`, { method: "POST" });
      setMessage(`Connected — balance ${info.balance.toFixed(2)} ${info.currency}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed");
    }
  }

  async function syncData(id: string) {
    setError(null);
    try {
      await apiJson("/market-data/sync", {
        method: "POST",
        body: JSON.stringify({
          broker_credential_id: id,
          symbol: "EURUSD",
          timeframes: ["M15", "H1", "H4"],
          count: 300,
        }),
      });
      setMessage("Synced EURUSD market data (M15/H1/H4, 300 bars).");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sync failed");
    }
  }

  return (
    <div>
      <h2>Broker Accounts</h2>
      <p className="hint">
        MT5 requires a Windows host with a running terminal; MT4 requires a bridge EA. Use{" "}
        <strong>paper</strong> to exercise the full connect → sync → backtest flow without live broker
        infrastructure.
      </p>
      {error && <p className="error">{error}</p>}
      {message && <p className="hint">{message}</p>}

      <form className="stacked-form" onSubmit={create}>
        <label htmlFor="broker-type">Broker type</label>
        <select id="broker-type" value={brokerType} onChange={(e) => setBrokerType(e.target.value)}>
          <option value="paper">Paper (demo, no real broker needed)</option>
          <option value="mt5">MetaTrader 5</option>
          <option value="mt4">MetaTrader 4</option>
        </select>

        <label htmlFor="broker-name">Broker name</label>
        <input id="broker-name" value={brokerName} onChange={(e) => setBrokerName(e.target.value)} required />

        {brokerType !== "paper" && (
          <>
            <label htmlFor="broker-server">Server</label>
            <input id="broker-server" value={server} onChange={(e) => setServer(e.target.value)} />
            <label htmlFor="broker-login">Login</label>
            <input id="broker-login" value={login} onChange={(e) => setLogin(e.target.value)} />
            <label htmlFor="broker-password">Password</label>
            <input
              id="broker-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </>
        )}

        <button type="submit" className="btn-primary">
          Add credential
        </button>
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Server</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {credentials.map((c) => (
            <tr key={c.id}>
              <td>{c.broker_name}</td>
              <td>{c.broker_type}</td>
              <td>{c.server || "—"}</td>
              <td className="actions">
                <button type="button" className="btn-secondary" onClick={() => testConnect(c.id)}>
                  Test connection
                </button>
                <button type="button" className="btn-secondary" onClick={() => syncData(c.id)}>
                  Sync EURUSD
                </button>
                <button type="button" className="btn-danger" onClick={() => remove(c.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
