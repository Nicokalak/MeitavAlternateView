import { defineConfig } from 'vitest/config';
import { resolve } from 'node:path';
import vue from '@vitejs/plugin-vue';
import Icons from 'unplugin-icons/vite';

const here = import.meta.dirname;
const backend = 'http://localhost:8080';

export default defineConfig({
  root: 'src',
  base: './',
  publicDir: resolve(here, 'src/public'),
  cacheDir: resolve(here, 'node_modules/.vite'),
  plugins: [vue(), Icons({ compiler: 'vue3' })],
  test: {
    root: here,
    environment: 'happy-dom',
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.APP_VERSION ?? 'dev'),
  },
  build: {
    outDir: resolve(here, '../src/meitav_view/static'),
    emptyOutDir: true,
    reportCompressedSize: false,
    rollupOptions: {
      input: {
        main: resolve(here, 'src/index.html'),
        unauthorized: resolve(here, 'src/401.html'),
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/portfolio': backend,
      '/trends': backend,
      '/marketState': backend,
      '/watchList': backend,
      '/ticker': backend,
      '/health': backend,
      '/version': backend,
    },
  },
});
