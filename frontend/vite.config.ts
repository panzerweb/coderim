import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { port: 5173, strictPort: true, proxy: { '/api': process.env.RELAY_API_PROXY || 'http://127.0.0.1:8000' } },
  build: { chunkSizeWarningLimit: 3000, rollupOptions: {output: {manualChunks(id) {
    if (id.includes('monaco-editor')) return 'monaco'
  }}} },
})
