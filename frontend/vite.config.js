import { defineConfig, loadEnv } from "vite";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const root = fileURLToPath(new URL("..", import.meta.url));
  const env = {
    ...loadEnv(mode, root, ""),
    ...loadEnv(mode, process.cwd(), ""),
    ...process.env,
  };
  const port = Number(env.BACKEND_PORT || 8001);
  const backend = env.BACKEND_URL || `http://127.0.0.1:${port}`;
  if (!/^https?:\/\//.test(backend))
    throw new Error("BACKEND_URL must be an HTTP(S) URL");
  return {
    plugins: [react()],
    server: {
      host: "127.0.0.1",
      port: Number(env.FRONTEND_PORT || 3000),
      strictPort: true,
      proxy: {
        "/api": {
          target: backend,
          changeOrigin: true,
        },
      },
    },
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./tests/setup.js",
      include: ["tests/**/*.test.{js,jsx}"],
      exclude: ["tests/**/*.spec.js", "node_modules"],
    },
  };
});
