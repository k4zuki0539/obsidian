param(
    [string]$TargetDate,
    [string]$TargetHour
)

# Screenpipe Raw Data Export Script
# Fetches OCR and audio transcription data from Screenpipe API and saves to markdown

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

# Configuration
$RawPath = Get-EnvValue -Name "SCREENPIPE_RAW_DIR" -Default "C:\ドキュメント\vault\screenpipe_all\raw"
$LogPath = Get-EnvValue -Name "SCREENPIPE_LOG_DIR" -Default "C:\ドキュメント\vault\screenpipe_all\logs"
$ApiUrl = Get-EnvValue -Name "SCREENPIPE_API_URL" -Default "http://localhost:3030"

# Determine target date and hour (default: previous hour)
if (-not $TargetDate -and -not $TargetHour) {
    $Now = Get-Date
    $PrevHour = $Now.AddHours(-1)
    $TargetDate = $PrevHour.ToString("yyyy-MM-dd")
    $TargetHour = $PrevHour.ToString("HH")
}

if (-not $TargetDate -or -not $TargetHour) {
    throw "TargetDate and TargetHour must be provided together"
}

if ($TargetDate -notmatch '^\d{4}-\d{2}-\d{2}$') {
    throw "TargetDate must be in yyyy-MM-dd format: $TargetDate"
}

if ($TargetHour -notmatch '^\d{2}$') {
    throw "TargetHour must be in HH format: $TargetHour"
}

# Log file
$LogFile = Join-Path $LogPath "export_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    Write-Host $LogMessage
}

try {
    # Create log directory
    if (-not (Test-Path $LogPath)) {
        New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
    }

    Write-Log "Starting Screenpipe data export..."
    Write-Log "Target: $TargetDate hour $TargetHour"

    # Calculate time range (UTC)
    $TargetDateTime = [DateTime]::ParseExact("$TargetDate $TargetHour", "yyyy-MM-dd HH", $null)
    $StartTime = $TargetDateTime.ToUniversalTime()
    $EndTime = $StartTime.AddHours(1)

    $StartTimeStr = $StartTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
    $EndTimeStr = $EndTime.ToString("yyyy-MM-ddTHH:mm:ssZ")

    Write-Log "Time range: $StartTimeStr to $EndTimeStr"

    # Fetch OCR data
    Write-Log "Fetching OCR data from Screenpipe API..."

    $OcrUrl = "$ApiUrl/search?content_type=ocr&start_time=$StartTimeStr&end_time=$EndTimeStr&limit=1000"
    try {
        $OcrResponse = Invoke-RestMethod -Uri $OcrUrl -Method Get -ContentType "application/json" -TimeoutSec 30
        $OcrData = $OcrResponse.data
        Write-Log "Retrieved $($OcrData.Count) OCR records"
    } catch {
        Write-Log "Warning: Failed to fetch OCR data: $($_.Exception.Message)"
        $OcrData = @()
    }

    # Fetch audio transcription data
    Write-Log "Fetching audio transcription data..."

    $AudioUrl = "$ApiUrl/search?content_type=audio&start_time=$StartTimeStr&end_time=$EndTimeStr&limit=1000"
    try {
        $AudioResponse = Invoke-RestMethod -Uri $AudioUrl -Method Get -ContentType "application/json" -TimeoutSec 30
        $AudioData = $AudioResponse.data
        Write-Log "Retrieved $($AudioData.Count) audio records"
    } catch {
        Write-Log "Warning: Failed to fetch audio data: $($_.Exception.Message)"
        $AudioData = @()
    }

    # Create output directory
    $OutputDir = Join-Path $RawPath $TargetDate
    if (-not (Test-Path $OutputDir)) {
        New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
    }

    $OutputFile = Join-Path $OutputDir "$TargetHour.md"

    # Generate markdown content
    $MarkdownContent = @"
# Screenpipe Raw Data - $TargetDate Hour $TargetHour

**Export Time**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Time Range**: $StartTimeStr to $EndTimeStr
**OCR Records**: $($OcrData.Count)
**Audio Records**: $($AudioData.Count)

---

## OCR Data

"@

    if ($OcrData.Count -gt 0) {
        foreach ($item in $OcrData) {
            $timestamp = $item.content.timestamp
            $appName = $item.content.app_name
            $windowName = $item.content.window_name
            $text = $item.content.text

            $MarkdownContent += @"

### $timestamp - $appName
**Window**: $windowName

``````
$text
``````

"@
        }
    } else {
        $MarkdownContent += "`n*No OCR data recorded for this hour*`n"
    }

    $MarkdownContent += @"

---

## Audio Transcriptions

"@

    if ($AudioData.Count -gt 0) {
        foreach ($item in $AudioData) {
            $timestamp = $item.content.timestamp
            $deviceName = if ($item.content.device_name) { $item.content.device_name } else { "Unknown Device" }
            $transcription = $item.content.transcription

            $MarkdownContent += @"

### $timestamp - $deviceName

``````
$transcription
``````

"@
        }
    } else {
        $MarkdownContent += "`n*No audio transcriptions recorded for this hour*`n"
    }

    # Save to file
    $MarkdownContent | Out-File -FilePath $OutputFile -Encoding UTF8

    Write-Log "Raw data exported to: $OutputFile"
    Write-Log "Export completed successfully"

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log "Stack Trace: $($_.ScriptStackTrace)"
    exit 1
}
