param(
    [string]$TargetDate
)

# Screenpipe Daily Summary Pipeline Script
# This script runs daily to aggregate hourly summaries

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
$HourlySummaryPath = Get-EnvValue -Name "SCREENPIPE_HOURLY_OUTPUT_DIR" -Required
$DailySummaryPath = Get-EnvValue -Name "SCREENPIPE_DAILY_OUTPUT_DIR" -Required
$CodexCommand = Get-EnvValue -Name "CODEX_COMMAND" -Required
$Timeout = [int](Get-EnvValue -Name "SCREENPIPE_SUMMARY_CODEX_TIMEOUT" -Default "600")
$MaxChars = [int](Get-EnvValue -Name "SCREENPIPE_SUMMARY_MAX_CHARS" -Default "20000")
$MaxLineLength = [int](Get-EnvValue -Name "SCREENPIPE_SUMMARY_MAX_LINE_LENGTH" -Default "400")
$LogPath = Get-EnvValue -Name "SCREENPIPE_LOG_DIR" -Default (Join-Path (Split-Path $DailySummaryPath -Parent) "logs")
$ExtraFlags = Get-EnvValue -Name "SCREENPIPE_CODEX_FLAGS" -Default ""

if (-not $TargetDate) {
    $TargetDate = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
}

if ($TargetDate -notmatch '^\d{4}-\d{2}-\d{2}$') {
    throw "TargetDate must be in yyyy-MM-dd format: $TargetDate"
}

# Log file
$LogFile = Join-Path $LogPath "daily_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

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

    Write-Log "Starting daily summary pipeline..."
    Write-Log "Processing date: $TargetDate"

    # Check hourly summaries exist
    $HourlyDir = Join-Path $HourlySummaryPath $TargetDate
    if (-not (Test-Path $HourlyDir)) {
        Write-Log "No hourly summaries found for: $TargetDate"
        exit 0
    }

    # Collect all hourly summaries
    $HourlyFiles = Get-ChildItem -Path $HourlyDir -Filter "*.md" | Sort-Object Name
    if ($HourlyFiles.Count -eq 0) {
        Write-Log "No hourly summary files found"
        exit 0
    }

    Write-Log "Found $($HourlyFiles.Count) hourly summaries"

    $AllSummaries = @()
    foreach ($File in $HourlyFiles) {
        $Hour = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
        $Content = Get-Content $File.FullName -Raw
        $AllSummaries += "## ${Hour}:00`n$Content"
    }

    $CombinedContent = $AllSummaries -join "`n`n---`n`n"
    $Lines = $CombinedContent -split "`r?`n"
    if ($MaxLineLength -gt 0) {
        $Lines = $Lines | ForEach-Object {
            if ($_.Length -gt $MaxLineLength) { $_.Substring(0, $MaxLineLength) } else { $_ }
        }
    }
    $TrimmedContent = $Lines -join "`n"
    if ($MaxChars -gt 0 -and $TrimmedContent.Length -gt $MaxChars) {
        $TrimmedContent = $TrimmedContent.Substring(0, $MaxChars)
    }

    # Generate daily summary with Codex
    Write-Log "Running Codex for daily summary generation..."

    $Prompt = @"
以下は${TargetDate}の時間別活動サマリーです。
これらを統合して、1日の活動レポートを日本語で作成してください。

必須:
- 概要
- タイムライン
- 作業内容
- 技術メモ
- 課題
- 次アクション候補
詳細度を保ち、行数を極端に削らないでください。

---
$TrimmedContent
---
"@

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
    $OutputFile = Join-Path $DailySummaryPath "$TargetDate.md"
    $Output | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Log "Daily summary saved to: $OutputFile"
    Write-Log "Daily summary pipeline completed successfully"

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

