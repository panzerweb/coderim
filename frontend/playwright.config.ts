import { defineConfig } from '@playwright/test'
import path from 'node:path'

const runtime = path.resolve('../.runtime/e2e', String(Date.now()))
const python = path.resolve(process.platform === 'win32' ? '../.venv/Scripts/python.exe' : '../.venv/bin/python')
export default defineConfig({
  testDir: './tests', testIgnore: '**/contest.spec.ts', timeout: 90_000, expect: {timeout: 15_000}, workers: 1,
  use: {baseURL: 'http://127.0.0.1:5173', headless: true, viewport: {width: 1440, height: 1000}, trace: 'retain-on-failure'},
  reporter: 'list',
  webServer: [
    {command: `"${python}" -m uvicorn app.main:app --app-dir "${path.resolve('../backend')}" --host 127.0.0.1 --port 8000`,
      url: 'http://127.0.0.1:8000/api/health', timeout: 120_000, reuseExistingServer: false,
      env: {RELAY_RUNTIME: runtime}},
    {command: 'npm run dev', url: 'http://127.0.0.1:5173', timeout: 120_000, reuseExistingServer: false},
  ],
})
