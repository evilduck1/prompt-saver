import { defineConfig } from 'vite';

export default defineConfig({
  clearScreen: false,
  server: { strictPort: true },
  css: { postcss: {} },
  build: { target: 'es2020', outDir: 'dist', emptyOutDir: true },
});
