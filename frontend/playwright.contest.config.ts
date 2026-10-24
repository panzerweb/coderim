import { defineConfig } from '@playwright/test'
import path from 'node:path'
const runtime=path.resolve('../.runtime/contest-e2e',String(Date.now()))
const python=path.resolve(process.platform==='win32'?'../.venv/Scripts/python.exe':'../.venv/bin/python')
export default defineConfig({
  testDir:'./tests',testMatch:'**/contest.spec.ts',outputDir:'./test-results-contest',timeout:180_000,expect:{timeout:15_000},workers:1,
  use:{baseURL:'http://127.0.0.1:5174',headless:true,viewport:{width:1440,height:1000},trace:'retain-on-failure'},reporter:'list',
  webServer:[
    {command:`"${python}" -m uvicorn contest_server:app --app-dir "${path.resolve('../backend/tests')}" --host 127.0.0.1 --port 8001`,url:'http://127.0.0.1:8001/api/health',timeout:120_000,reuseExistingServer:false,env:{RELAY_RUNTIME:runtime,RELAY_TEST_SERVER:'yes',RELAY_TEST_EXECUTOR:'local'}},
    {command:'npm run dev -- --port 5174',url:'http://127.0.0.1:5174',timeout:120_000,reuseExistingServer:false,env:{RELAY_API_PROXY:'http://127.0.0.1:8001',VITE_API_BASE_URL:''}},
  ],
})
