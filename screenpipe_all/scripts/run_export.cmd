@echo off
setlocal
set SCREENPIPE_RAW_DIR=C:\ドキュメント\vault\screenpipe_all\raw
set SCREENPIPE_LOG_DIR=C:\ドキュメント\vault\screenpipe_all\logs
set SCREENPIPE_API_URL=http://localhost:3030
pwsh.exe -ExecutionPolicy Bypass -File "C:\ドキュメント\vault\screenpipe_all\scripts\export_raw.ps1"
endlocal
