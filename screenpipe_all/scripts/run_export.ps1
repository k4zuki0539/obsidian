# Screenpipe Export Wrapper Script
# Sets environment variables and invokes export_raw.ps1

$ErrorActionPreference = "Stop"

# Set environment variables
$env:SCREENPIPE_RAW_DIR = "C:\ドキュメント\vault\screenpipe_all\raw"
$env:SCREENPIPE_LOG_DIR = "C:\ドキュメント\vault\screenpipe_all\logs"
$env:SCREENPIPE_API_URL = "http://localhost:3030"

# Execute export script
& "C:\ドキュメント\vault\screenpipe_all\scripts\export_raw.ps1"
