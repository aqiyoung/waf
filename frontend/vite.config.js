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
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加X-Forwarded-For和X-Real-IP头，传递真实的客户端IP地址
            const clientIP = req.connection.remoteAddress || req.socket.remoteAddress;
            proxyReq.setHeader('X-Forwarded-For', clientIP);
            proxyReq.setHeader('X-Real-IP', clientIP);
          });
        }
      }
    }
  }
})
