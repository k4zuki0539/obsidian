param(
    [string]$TargetDate,
    [string]$TargetHour
)

# Screenpipe Hourly Summary Pipeline Script
# This script runs every hour to generate hourly summaries

$ErrorActionPreference = "Stop"

function Get-EnvValue {
    param(
        [string]$Name,
        [string]$Default = $null,
        [switch]$Required
    )
    $Value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if (-not $Value) { $Value = [Environment]::GetEnvironmentVariable($Name, "User") }
    if (-not $Value) { $Value = [Environment]::GetEnvironmentVariable($Name, "Machine") }
    if (-not $Value -and $Required) {
        throw "Missing required environment variable: $Name"
    }
    if (-not $Value) { $Value = $Default }
    return $Value
}

# Configuration via environment variables
$RawPath = Get-EnvValue -Name "SCREENPIPE_RAW_DIR" -Required
$HourlySummaryPath = Get-EnvValue -Name "SCREENPIPE_HOURLY_OUTPUT_DIR" -Required
$CodexCommand = Get-EnvValue -Name "CODEX_COMMAND" -Required
$Timeout = [int](Get-EnvValue -Name "SCREENPIPE_SUMMARY_CODEX_TIMEOUT" -Default "600")
$MaxChars = [int](Get-EnvValue -Name "SCREENPIPE_SUMMARY_MAX_CHARS" -Default "20000")
$MaxLineLength = [int](Get-EnvValue -Name "SCREENPIPE_SUMMARY_MAX_LINE_LENGTH" -Default "400")
$LogPath = Get-EnvValue -Name "SCREENPIPE_LOG_DIR" -Default (Join-Path (Split-Path $HourlySummaryPath -Parent) "logs")
$ExtraFlags = Get-EnvValue -Name "SCREENPIPE_CODEX_FLAGS" -Default ""

if (-not $TargetDate -and -not $TargetHour) {
    $Now = Get-Date
    $TargetDate = $Now.AddHours(-1).ToString("yyyy-MM-dd")
    $TargetHour = $Now.AddHours(-1).ToString("HH")
}

if (-not $TargetDate -or -not $TargetHour) {
    throw "TargetDate and TargetHour must be provided together (e.g., -TargetDate 2025-01-01 -TargetHour 13)."
}

if ($TargetDate -notmatch '^\d{4}-\d{2}-\d{2}$') {
    throw "TargetDate must be in yyyy-MM-dd format: $TargetDate"
}

if ($TargetHour -notmatch '^\d{2}$') {
    throw "TargetHour must be in HH format: $TargetHour"
}

# Log file
$LogFile = Join-Path $LogPath "hourly_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    Write-Host $LogMessage
}

try {
    if (-not (Test-Path $LogPath)) {
        New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
    }

    Write-Log "Starting hourly summary pipeline..."
    Write-Log "Processing: $TargetDate hour $TargetHour"

    # Check raw log exists
    $RawFile = Join-Path $RawPath "$TargetDate\$TargetHour.md"
    if (-not (Test-Path $RawFile)) {
        Write-Log "Raw log not found: $RawFile"
        exit 0
    }

    # Create output directory
    $OutputDir = Join-Path $HourlySummaryPath $TargetDate
    if (-not (Test-Path $OutputDir)) {
        New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
    }

    $OutputFile = Join-Path $OutputDir "$TargetHour.md"

    # Run Codex to generate summary
    Write-Log "Running Codex for summary generation..."
    
    $RawContent = Get-Content $RawFile -Raw
    $Lines = $RawContent -split "`r?`n"
    if ($MaxLineLength -gt 0) {
        $Lines = $Lines | ForEach-Object {
            if ($_.Length -gt $MaxLineLength) { $_.Substring(0, $MaxLineLength) } else { $_ }
        }
    }
    $TrimmedContent = $Lines -join "`n"
    if ($MaxChars -gt 0 -and $TrimmedContent.Length -gt $MaxChars) {
        $TrimmedContent = $TrimmedContent.Substring(0, $MaxChars)
    }

    $Prompt = @"
以下のScreenpipeログから、この1時間の活動サマリーを日本語で作成してください。

必須:
- 具体的なファイル名/コマンド/URLは省略せず残す
- 機密値（APIキー/トークン/パスワードなど）は [REDACTED] に置換
- 重要なアクティビティ、使用アプリ、キーワードを含める
- 箇条書きを中心に簡潔にまとめる

---
$TrimmedContent
---
"@

    # Execute Codex
    $CodexArgs = "--skip-git-repo-check"
    if ($ExtraFlags) {
        $CodexArgs = "$CodexArgs $ExtraFlags"
    }
    $CodexArgs = "$CodexArgs --timeout $Timeout"

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $CodexCommand
    $StartInfo.Arguments = $CodexArgs
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardInput = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.CreateNoWindow = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo
    $Process.Start() | Out-Null
    
    $Process.StandardInput.WriteLine($Prompt)
    $Process.StandardInput.Close()

    $Output = $Process.StandardOutput.ReadToEnd()
    $ErrorOutput = $Process.StandardError.ReadToEnd()

    if (-not $Process.WaitForExit(($Timeout * 1000))) {
        $Process.Kill()
        throw "Codex timed out after $Timeout seconds"
    }

    if ($Process.ExitCode -ne 0) {
        Write-Log "Codex error: $ErrorOutput"
        throw "Codex failed with exit code $($Process.ExitCode)"
    }

    # Save output
    $Output | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Log "Summary saved to: $OutputFile"
    Write-Log "Hourly summary pipeline completed successfully"

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

