import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import vueDevTools from "vite-plugin-vue-devtools";

export default defineConfig(({ mode }) => ({
  base: process.env.BASE_URL,
  plugins: [vue(), vueDevTools(), tailwindcss()],
  css: {
    devSourcemap: mode === "development",
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    sourcemap: true,
  },
  // This is what the proxy block looks like based on your previous messages
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/files": {
        target: "http://127.0.0.1:8005",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/files/, ""),
        // rewrite: (path) => path.replace(/^\/files/, ""),
      },
    },
  },
}));
