import {  defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: 'https://127.0.0.1:8000', // ✅ Correct backend URL
        changeOrigin: true,
        secure: false,  // ✅ Ignore SSL issues in local development
      },
    },
  }
})
