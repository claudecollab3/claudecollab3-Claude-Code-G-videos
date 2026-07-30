import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // The shorthand string form doesn't proxy WebSocket upgrade
      // requests (needed for /api/v1/notifications/ws); ws: true does.
      "/api": {
        target: "http://localhost:8000",
        ws: true,
      },
    },
  },
});
