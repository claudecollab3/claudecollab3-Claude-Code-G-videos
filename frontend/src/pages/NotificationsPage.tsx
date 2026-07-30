import React, { useEffect, useState } from "react";
import { apiJson } from "../api";
import { useNotifications } from "../hooks/useNotifications";

interface Preferences {
  channels: Record<string, boolean>;
}

interface LogEntry {
  event: string;
  channel: string;
  success: boolean;
  title: string;
  body: string;
  created_at: string;
}

const CHANNEL_LABELS: Record<string, string> = {
  desktop: "Desktop (in-app)",
  push: "Push (in-app)",
  telegram: "Telegram",
  discord: "Discord",
  email: "Email",
};

export default function NotificationsPage() {
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [history, setHistory] = useState<LogEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { messages, requestDesktopPermission } = useNotifications();

  function load() {
    apiJson<Preferences>("/notifications/preferences")
      .then(setPreferences)
      .catch((err: Error) => setError(err.message));
    apiJson<LogEntry[]>("/notifications/history")
      .then(setHistory)
      .catch(() => undefined);
  }

  useEffect(load, []);

  async function toggle(channel: string, enabled: boolean) {
    try {
      const updated = await apiJson<Preferences>("/notifications/preferences", {
        method: "PATCH",
        body: JSON.stringify({ channel, enabled }),
      });
      setPreferences(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update preference");
    }
  }

  async function sendTest() {
    setError(null);
    try {
      await apiJson("/notifications/test", {
        method: "POST",
        body: JSON.stringify({
          event: "trade_opened",
          title: "Test notification",
          body: "This is a test notification from the dashboard.",
        }),
      });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test notification failed");
    }
  }

  return (
    <div>
      <h2>Notifications</h2>
      {error && <p className="error">{error}</p>}

      <button type="button" className="btn-secondary" onClick={requestDesktopPermission}>
        Enable browser desktop notifications
      </button>

      {preferences && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Channel</th>
              <th>Enabled</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(preferences.channels).map(([channel, enabled]) => (
              <tr key={channel}>
                <td>{CHANNEL_LABELS[channel] ?? channel}</td>
                <td>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={enabled}
                      onChange={(e) => toggle(channel, e.target.checked)}
                    />
                    <span className="slider" />
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button type="button" className="btn-primary" onClick={sendTest}>
        Send test notification
      </button>

      <h3>Live feed (this session)</h3>
      <ul className="feed">
        {messages.length === 0 && <li className="hint">No live notifications yet.</li>}
        {messages.map((m, i) => (
          <li key={i}>
            <strong>{m.title}</strong> — {m.body}
          </li>
        ))}
      </ul>

      <h3>History</h3>
      {history.length === 0 ? (
        <p className="hint">No notifications dispatched yet.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Event</th>
              <th>Channel</th>
              <th>Status</th>
              <th>When</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h, i) => (
              <tr key={i}>
                <td>{h.event.replace(/_/g, " ")}</td>
                <td>{h.channel}</td>
                <td className={h.success ? "positive" : "negative"}>{h.success ? "Sent" : "Failed"}</td>
                <td>{new Date(h.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
