# Check all Screenpipe tasks
Get-ScheduledTask -TaskName "Screenpipe*" | ForEach-Object {
    $info = Get-ScheduledTaskInfo -TaskName $_.TaskName
    [PSCustomObject]@{
        Name = $_.TaskName
        State = $_.State
        LastRun = $info.LastRunTime
        LastResult = $info.LastTaskResult
        NextRun = $info.NextRunTime
    }
} | Format-Table -AutoSize
