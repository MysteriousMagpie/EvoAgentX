import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createRequire } from 'module';

// Use createRequire to load CommonJS PostCSS config
const requireCjs = createRequire(import.meta.url);
const postcssConfig = requireCjs('./postcss.config.cjs');

export default defineConfig({
  css: { postcss: postcssConfig },
  plugins: [react()],
  server: {
    port: 5173,
  },
});
