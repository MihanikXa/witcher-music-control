# Read-only, one-shot witness. Does not launch a process or save a trace.
# Dot-source only for unit tests; normal invocation prints privacy-filtered JSON.
function Get-WmcGameArgumentWitness {
    try {
        $wmcProcesses = @(Get-CimInstance -ClassName Win32_Process -Filter "Name='witcher3.exe'" -ErrorAction Stop)
    } catch {
        # Exception text may contain private information; deliberately omit it.
        return [pscustomobject]@{ Status = 'QueryFailed'; Processes = @() }
    }
    $wmcRows = @(
        foreach ($wmcProcess in $wmcProcesses) {
            $wmcFlag = $null
            if (-not [string]::IsNullOrWhiteSpace($wmcProcess.CommandLine)) {
                # Match the pinned native strstr: case-sensitive SUBSTRING, not token parsing.
                $wmcFlag = ([string]$wmcProcess.CommandLine).Contains('-debugscripts')
            }
            [pscustomobject]@{
                ExecutablePath = $wmcProcess.ExecutablePath
                DebugScriptsSubstringPresent = $wmcFlag
            }
        }
    )
    $wmcStatus = 'Observed'
    if ($wmcRows.Count -eq 0) { $wmcStatus = 'NotRunning' }
    elseif ($wmcRows.Count -gt 1) { $wmcStatus = 'MultipleGameProcesses' }
    elseif ($null -eq $wmcRows[0].DebugScriptsSubstringPresent -or
            [string]::IsNullOrWhiteSpace($wmcRows[0].ExecutablePath)) { $wmcStatus = 'Unreadable' }
    return [pscustomobject]@{ Status = $wmcStatus; Processes = $wmcRows }
}

if ($MyInvocation.InvocationName -ne '.') {
    Get-WmcGameArgumentWitness | ConvertTo-Json -Depth 4
}
