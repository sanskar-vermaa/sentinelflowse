$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\..\apps\api"
if (!(Test-Path ".env")) {
  Copy-Item ".env.demo.example" ".env"
}
python -m app.db.seed
uvicorn app.main:app --reload
