import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// UI ONLY: this React app calls the SAME backend as the legacy app, proxied in dev.
// Point the targets at wherever the legacy backend runs (e.g. local Tomcat on :8080).
// Add more entries if the legacy app calls other paths.
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE || '/',
  server: {
    port: 5173,
    host: '127.0.0.1',
    strictPort: true,
    proxy: {
      // Use 127.0.0.1 (NOT 0.0.0.0, NOT localhost-as-IPv6) — the legacy app binds IPv4 on :8080.
      '/BAA': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/eisl': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    },
  },
  preview: { port: 5173, host: '127.0.0.1', strictPort: true },
})
