import { defineConfig, devices } from "@playwright/test";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";
const root = fileURLToPath(new URL("..", import.meta.url));
const candidate = fileURLToPath(
  new URL(
    "../backend/.venv/" +
      (process.platform === "win32" ? "Scripts/python.exe" : "bin/python"),
    import.meta.url,
  ),
);
const python =
  process.env.PYTHON || (existsSync(candidate) ? candidate : "python");
const backendPort = Number(process.env.E2E_BACKEND_PORT || 8101);
const frontendPort = Number(process.env.E2E_FRONTEND_PORT || 3001);
const baseURL =
  process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${frontendPort}`;
export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.js",
  timeout: 60000,
  workers: 2,
  use: {
    baseURL,
    headless: true,
    actionTimeout: 15000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : [
        {
          command: `"${python}" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port ${backendPort} --no-access-log`,
          cwd: root,
          url: `http://127.0.0.1:${backendPort}/health`,
          reuseExistingServer: false,
          timeout: 60000,
          env: {
            SIMPLIFIER_LOAD_DOTENV: "0",
            ENVIRONMENT: "development",
            AUTH_MODE: "local",
            SUPABASE_URL: "",
            SUPABASE_PUBLISHABLE_KEY: "",
            GOOGLE_MAPS_SERVER_KEY: "",
            CORS_ORIGINS: baseURL,
            APP_DATA_DIR: fileURLToPath(
              new URL(`../artifacts/e2e-state-${Date.now()}`, import.meta.url),
            ),
          },
        },
        {
          command: `npm${process.platform === "win32" ? ".cmd" : ""} run dev`,
          url: baseURL + "/api/v1/auth/configuration",
          reuseExistingServer: false,
          timeout: 60000,
          env: {
            FRONTEND_PORT: String(frontendPort),
            BACKEND_PORT: String(backendPort),
            BACKEND_URL: `http://127.0.0.1:${backendPort}`,
          },
        },
      ],
});
