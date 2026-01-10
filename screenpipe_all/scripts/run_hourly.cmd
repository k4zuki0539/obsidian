@echo off
setlocal
set CODEX_COMMAND=C:\Users\PC_User\AppData\Roaming\npm\codex.cmd
set SCREENPIPE_RAW_DIR=C:\ドキュメント\vault\screenpipe_all\raw
set SCREENPIPE_HOURLY_OUTPUT_DIR=C:\ドキュメント\vault\screenpipe_all\hourly_summary
set SCREENPIPE_DAILY_OUTPUT_DIR=C:\ドキュメント\vault\screenpipe_all\daily_summary
set SCREENPIPE_LOG_DIR=C:\ドキュメント\vault\screenpipe_all\logs
set SCREENPIPE_SUMMARY_CODEX_TIMEOUT=600
set SCREENPIPE_CODEX_FLAGS=--dangerously-bypass-approvals-and-sandbox
pwsh.exe -ExecutionPolicy Bypass -File "C:\ドキュメント\vault\screenpipe_all\scripts\hourly_summary.ps1"
endlocal
