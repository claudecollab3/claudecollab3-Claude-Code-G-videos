# notifications/

Multi-channel notification dispatch, built out in **Phase 7**.

```
notifications/
  dispatcher.py    Fan-out event -> enabled channels, per-user preferences
  channels/
    telegram.py
    discord.py
    email.py
    push.py        Web push (for the dashboard) / mobile push
    desktop.py      Desktop notifications (dashboard WebSocket -> Notification API)
  events.py         Notification event types: trade opened/closed, TP/SL hit,
                    high-impact news, trading paused, broker disconnected,
                    large drawdown, daily goal reached
```
