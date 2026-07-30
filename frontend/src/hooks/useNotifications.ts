import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "../api";

export interface NotificationPayload {
  event: string;
  title: string;
  body: string;
  data: Record<string, unknown>;
}

export function useNotifications() {
  const [messages, setMessages] = useState<NotificationPayload[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return undefined;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(
      `${protocol}://${window.location.host}/api/v1/notifications/ws?token=${encodeURIComponent(token)}`,
    );
    socketRef.current = socket;

    socket.onmessage = (event: MessageEvent<string>) => {
      const payload = JSON.parse(event.data) as NotificationPayload;
      setMessages((prev) => [payload, ...prev].slice(0, 20));
      if (typeof Notification !== "undefined" && Notification.permission === "granted") {
        new Notification(payload.title, { body: payload.body });
      }
    };

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, []);

  const requestDesktopPermission = useCallback(() => {
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      void Notification.requestPermission();
    }
  }, []);

  return { messages, requestDesktopPermission };
}
