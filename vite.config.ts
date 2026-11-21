import { defineConfig } from 'vite'

export default defineConfig({
  base: './',
  esbuild: { jsx: 'automatic' },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('/hook-library/seeds/short/')) return 'short-hook-catalog'
          if (id.includes('/hook-library/seeds/long/')) return 'long-hook-catalog'
          if (id.includes('/creator-hooks/')) return 'creator-hooks'
        },
      },
    },
  },
})
