import React, { useState } from "react";
import Layout, { TabId } from "./components/Layout";
import { AuthProvider, useAuth } from "./context/AuthContext";
import AiPage from "./pages/AiPage";
import BacktestPage from "./pages/BacktestPage";
import BrokerPage from "./pages/BrokerPage";
import LoginPage from "./pages/LoginPage";
import NewsPage from "./pages/NewsPage";
import NotificationsPage from "./pages/NotificationsPage";
import OverviewPage from "./pages/OverviewPage";
import SignalsPage from "./pages/SignalsPage";
import StrategiesPage from "./pages/StrategiesPage";
import "./styles.css";

function Dashboard() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState<TabId>("overview");

  if (!user) return null;

  return (
    <Layout active={tab} onSelect={setTab} userEmail={user.email} onLogout={logout}>
      {tab === "overview" && <OverviewPage />}
      {tab === "strategies" && <StrategiesPage />}
      {tab === "signals" && <SignalsPage />}
      {tab === "ai" && <AiPage />}
      {tab === "news" && <NewsPage />}
      {tab === "backtest" && <BacktestPage />}
      {tab === "broker" && <BrokerPage />}
      {tab === "notifications" && <NotificationsPage />}
    </Layout>
  );
}

function Root() {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-screen">Loading...</div>;
  return user ? <Dashboard /> : <LoginPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <Root />
    </AuthProvider>
  );
}
