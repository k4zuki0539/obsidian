# Remove duplicate tasks
Unregister-ScheduledTask -TaskName "Screenpipe Hourly Summary" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "Screenpipe Daily Summary" -Confirm:$false -ErrorAction SilentlyContinue
Write-Output "Duplicate tasks removed"
