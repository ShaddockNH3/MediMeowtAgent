import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools' // 保留医生端的开发工具（可选，不影响核心功能）

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(), // 患者端配置已有
    vueDevTools(), // 保留医生端的开发工具（方便调试，不想用可以删掉）
  ],
  resolve: {
    alias: {
      // 保留医生端的别名配置（关键！否则医生端代码中 import '@/xxx' 会报错）
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // 完全复用患者端的代理配置，一字不改
      '/api': {
        target: 'http://124.221.70.136:11391',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    }
  }
});