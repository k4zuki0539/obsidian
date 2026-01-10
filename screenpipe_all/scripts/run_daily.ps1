# Daily summary runner wrapper
$ErrorActionPreference = "Stop"

# Set environment variables
$env:CODEX_COMMAND = "C:\Users\PC_User\AppData\Roaming\npm\codex.cmd"
$env:SCREENPIPE_RAW_DIR = "C:\ドキュメント\vault\screenpipe_all\raw"
$env:SCREENPIPE_HOURLY_OUTPUT_DIR = "C:\ドキュメント\vault\screenpipe_all\hourly_summary"
$env:SCREENPIPE_DAILY_OUTPUT_DIR = "C:\ドキュメント\vault\screenpipe_all\daily_summary"
$env:SCREENPIPE_LOG_DIR = "C:\ドキュメント\vault\screenpipe_all\logs"
$env:SCREENPIPE_SUMMARY_CODEX_TIMEOUT = "600"
$env:SCREENPIPE_CODEX_FLAGS = "--dangerously-bypass-approvals-and-sandbox"

# Run daily summary script
& "C:\ドキュメント\vault\screenpipe_all\scripts\daily_summary.ps1"


