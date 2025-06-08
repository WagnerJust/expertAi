import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow external connections (Tailscale)
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://backend:8000', // Proxy API calls to backend in Docker
        changeOrigin: true,
      }
    }
  },
  preview: {
    host: '0.0.0.0', // Allow external connections for preview mode
    port: 3000
  },
  test: {
    environment: 'jsdom',
    globals: true
  },
})
