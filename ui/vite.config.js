import { defineConfig } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';

/**
 * Dev-only: the manifest's icon paths are written for the built layout
 * (assets/site.webmanifest -> assets/favicon/*). Serve them from /favicon/* here.
 */
const manifestIconDevRewrite = () => ({
  name: 'manifest-icon-dev-rewrite',
  apply: 'serve',
  configureServer(server) {
    server.middlewares.use((req, _res, next) => {
      if (req.url?.startsWith('/favicon/favicon/')) {
        req.url = req.url.replace('/favicon/favicon/', '/favicon/');
      }
      next();
    });
  },
});

export default defineConfig({
  root: 'src',
  base: './',
  plugins: [vue(), manifestIconDevRewrite()],
  test: {
    root: resolve(import.meta.dirname),
    environment: 'happy-dom',
  },
  define: {
    global: 'window',
  },
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