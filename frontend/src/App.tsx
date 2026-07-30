import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  app_name: string;
  app_env: string;
  trading_mode: string;
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/health")
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => setError("Backend unreachable"));
  }, []);

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Trading Bot</h1>
      <p>
        Dashboard placeholder — the full live dashboard (balance, equity,
        trades, AI confidence, news, heat map) lands in Phase 7.
      </p>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {health && (
        <pre>{JSON.stringify(health, null, 2)}</pre>
      )}
    </main>
  );
}
