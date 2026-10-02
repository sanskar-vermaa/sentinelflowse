$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\..\apps\web"
if (!(Test-Path "node_modules")) {
  npm ci
}
npm run dev
