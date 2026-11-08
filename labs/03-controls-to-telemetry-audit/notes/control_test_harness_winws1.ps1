# Run only in a disposable Windows lab; restore its snapshot after checking telemetry.
[CmdletBinding(SupportsShouldProcess)]
param([switch]$Commit)

$ErrorActionPreference = 'Stop'
$User = 'lab03_user'
$TaskPath = '\Lab03\'
$TaskName = 'CanaryTask'

if (-not $Commit) {
    Write-Output 'Preview: attempt a failed local logon, create a disabled test user, add it to Administrators, create a SYSTEM canary task, and enable Security Group Management auditing. Use -Commit to apply, or -Commit -WhatIf to preview.'
    return
}
if (-not $PSCmdlet.ShouldProcess($env:COMPUTERNAME, 'Generate Lab03 audit events and change local accounts, task and audit policy')) {
    return
}

# Check conflicts before making changes; never replace an existing user or task.
if (Get-LocalUser | Where-Object Name -eq $User) {
    throw "Local user $User already exists. Use a fresh lab snapshot."
}
if (Get-ScheduledTask | Where-Object { $_.TaskPath -eq $TaskPath -and $_.TaskName -eq $TaskName }) {
    throw 'The Lab03 canary task already exists. Use a fresh lab snapshot.'
}
$Password = Read-Host 'Choose a unique password for the disabled lab account' -AsSecureString

try {
    # Failure is intentional here. Event delivery depends on audit policy and collection.
    & cmd.exe /c 'net use \\localhost\ipc$ /user:lab03_user IntentionallyWrongLabPassword >nul 2>&1'

    New-LocalUser -Name $User -Password $Password -Disabled | Out-Null
    Add-LocalGroupMember -SID 'S-1-5-32-544' -Member $User

    & schtasks.exe /Create /TN "$TaskPath$TaskName" /SC ONCE /ST 23:59 /TR 'cmd.exe /c whoami > C:\Windows\Temp\lab03_canary.txt' /RU SYSTEM
    if ($LASTEXITCODE -ne 0) { throw "Scheduled task creation failed (exit $LASTEXITCODE)." }

    & auditpol.exe /set '/subcategory:Security Group Management' /success:enable /failure:enable
    if ($LASTEXITCODE -ne 0) { throw "Audit policy update failed (exit $LASTEXITCODE)." }

    Write-Output 'Lab actions completed. Check Sentinel for the expected events, then restore the disposable VM snapshot.'
}
catch {
    throw "Lab harness stopped. Earlier changes may remain; inspect the VM or restore its snapshot. $($_.Exception.Message)"
}
