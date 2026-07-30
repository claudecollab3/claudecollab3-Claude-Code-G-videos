# frontend/

Web dashboard, built out in **Phase 7** (React + TypeScript + Vite).

```
frontend/src/
  api.ts                Token storage + fetch wrapper (401 -> refresh -> retry)
  context/AuthContext.tsx   Auth state (login/register/logout, current user)
  hooks/useNotifications.ts WebSocket hook for the live notification feed
  components/
    Layout.tsx          Sidebar navigation + topbar (tab-based, no react-router)
    EquityCurveChart.tsx  Hand-rolled SVG equity curve chart
  pages/
    LoginPage.tsx, OverviewPage.tsx, StrategiesPage.tsx, SignalsPage.tsx,
    AiPage.tsx, NewsPage.tsx, BacktestPage.tsx, BrokerPage.tsx,
    NotificationsPage.tsx
  styles.css            Dark theme
```

`vite.config.ts` proxies `/api` to the backend in dev, including WebSocket
upgrades (`ws: true` — the shorthand string proxy form silently drops WS
upgrade requests). In the production Docker image, `docker/nginx.conf`
does the same job in front of the built static bundle.

## Development

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173, proxies /api to :8000
npm run build     # type-checks (tsc) and produces dist/
```
