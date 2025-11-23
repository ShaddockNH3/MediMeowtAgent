// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue'; // ⚡ 1. 导入 vue 插件

export default defineConfig({
  // ⚡ 2. 在 plugins 数组中启用 vue()
  plugins: [
    vue(), 
  ],
  server: {
    // 确保端口是你想要的，比如 8000
    // 如果 8000 被占用，Vite 会自动尝试 8001，这是正常的
    port: 8002, 
    // ⚡ 我们之前的结论是代理有问题，所以可以暂时注释掉或删除
    // proxy: {
    //   '/api': {
    //     target: 'http://124.221.70.136:11391',
    //     changeOrigin: true,
    //     rewrite: (path) => path.replace(/^\/api/, ''),
    //   },
    // },
  },
})