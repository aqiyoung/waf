import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8009',
        changeOrigin: true
      }
    },
    middleware: [
      (req, res, next) => {
        // Add CSP header to allow Vite's HMR
        res.setHeader('Content-Security-Policy', "script-src 'self' 'unsafe-eval' 'unsafe-inline';");
        next();
      }
    ]
  }
})
