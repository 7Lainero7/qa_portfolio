import { defineConfig, devices } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

// Простейший загрузчик .env (без внешних зависимостей): e2e/.env
const envFile = path.join(__dirname, ".env");
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, "utf-8").split("\n")) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (match && process.env[match[1]] === undefined) {
      process.env[match[1]] = match[2].replace(/^["']|["']$/g, "");
    }
  }
}

const API_URL = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";
const UI_URL = process.env.E2E_UI_URL ?? "http://localhost:5173";
// Порт из E2E_UI_URL (для webServer), по умолчанию 5173
const uiPort = Number(new URL(UI_URL).port || 5173);

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],

  use: {
    baseURL: UI_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  // Автоматически запускать frontend перед тестами
  webServer: [
    {
      command: "npm run dev --prefix ../frontend",
      port: uiPort,
      reuseExistingServer: true,
      timeout: 30_000,
    },
  ],
});