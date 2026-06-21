import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base: '/' standalone (default). To embed in the legacy JSP shell exactly like the
// original, set VITE_BASE=/BAA/businessAnalysisNext/ (and match react_base_path in the
// verify kit's config.json).
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE || '/',
  server: { port: 5173, host: '127.0.0.1', strictPort: true },
  preview: { port: 5173, host: '127.0.0.1', strictPort: true },
})
