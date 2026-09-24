import { defineConfig } from 'vite';
import { resolve } from 'path';
import inject from '@rollup/plugin-inject';

export default defineConfig({
  root: 'src',
  base: './',
  define: {
    global: 'window',
  },
  plugins: [
    inject({
      jQuery: 'jquery',
      $: 'jquery',
      include: ['**/*.js'],
    }),
  ],
  build: {
    outDir: resolve(import.meta.dirname, 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(import.meta.dirname, 'src/index.html'),
        unauthorized: resolve(import.meta.dirname, 'src/401.html'),
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/portfolio': 'http://localhost:8080',
      '/trends': 'http://localhost:8080',
      '/marketState': 'http://localhost:8080',
      '/watchList': 'http://localhost:8080',
      '/ticker': 'http://localhost:8080',
      '/health': 'http://localhost:8080',
    },
  },
});
