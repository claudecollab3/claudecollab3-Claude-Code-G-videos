import React, { ReactNode } from "react";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "strategies", label: "Strategies" },
  { id: "signals", label: "Signals" },
  { id: "ai", label: "AI Predictions" },
  { id: "news", label: "News" },
  { id: "backtest", label: "Backtesting" },
  { id: "broker", label: "Broker" },
  { id: "notifications", label: "Notifications" },
] as const;

export type TabId = (typeof TABS)[number]["id"];

interface LayoutProps {
  active: TabId;
  onSelect: (tab: TabId) => void;
  userEmail: string;
  onLogout: () => void;
  children: ReactNode;
}

export default function Layout({ active, onSelect, userEmail, onLogout, children }: LayoutProps) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">Trading Bot</div>
        <nav>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={tab.id === active ? "nav-item active" : "nav-item"}
              onClick={() => onSelect(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </aside>
      <div className="main">
        <header className="topbar">
          <span className="user-email">{userEmail}</span>
          <button type="button" className="btn-secondary" onClick={onLogout}>
            Log out
          </button>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
