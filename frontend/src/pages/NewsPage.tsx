import React, { useEffect, useState } from "react";
import { apiJson } from "../api";

interface CalendarEvent {
  external_id: string;
  name: string;
  currency: string;
  impact: string;
  event_time: string;
  forecast: string | null;
  previous: string | null;
  actual: string | null;
}

interface NewsPolicyResult {
  action: string;
  reason: string;
  upcoming_event: CalendarEvent | null;
}

export default function NewsPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [symbol, setSymbol] = useState("EURUSD");
  const [policy, setPolicy] = useState<NewsPolicyResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiJson<CalendarEvent[]>("/news/upcoming")
      .then(setEvents)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function checkPolicy(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const result = await apiJson<NewsPolicyResult>("/news/policy", {
        method: "POST",
        body: JSON.stringify({ symbol }),
      });
      setPolicy(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to check news policy");
    }
  }

  return (
    <div>
      <h2>Economic Calendar</h2>
      {error && <p className="error">{error}</p>}
      {events.length === 0 && (
        <p className="hint">
          No calendar provider configured (ECONOMIC_CALENDAR_API_KEY / ECONOMIC_CALENDAR_BASE_URL) —
          no vendor is wired in by default, so there are no upcoming events to show.
        </p>
      )}
      {events.length > 0 && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Event</th>
              <th>Currency</th>
              <th>Impact</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {events.map((ev) => (
              <tr key={ev.external_id}>
                <td>{ev.name}</td>
                <td>{ev.currency}</td>
                <td>{ev.impact}</td>
                <td>{new Date(ev.event_time).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h3>News Policy Check</h3>
      <p className="hint">Trade / Wait / Reduce risk / Close existing, based on upcoming high-impact news.</p>
      <form className="inline-form" onSubmit={checkPolicy}>
        <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="EURUSD" />
        <button type="submit" className="btn-primary">
          Check
        </button>
      </form>
      {policy && (
        <div className="card">
          <p>
            Action: <strong>{policy.action.replace(/_/g, " ").toUpperCase()}</strong>
          </p>
          <p className="muted">{policy.reason}</p>
        </div>
      )}
    </div>
  );
}
