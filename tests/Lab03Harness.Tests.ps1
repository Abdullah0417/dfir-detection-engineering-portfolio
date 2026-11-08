BeforeAll {
    $Harness = Join-Path $PSScriptRoot '../labs/03-controls-to-telemetry-audit/notes/control_test_harness_winws1.ps1'
    # Stubs keep these tests independent of Windows account and task modules.
    function Get-LocalUser { }
    function Get-ScheduledTask { }
    function New-LocalUser { param($Name, $Password, [switch]$Disabled) }
    function Add-LocalGroupMember { param($SID, $Member) }
    function cmd.exe { }
    function schtasks.exe { }
    function auditpol.exe { }
}

Describe 'Lab03 harness safety' {
    BeforeEach {
        Mock Get-LocalUser { }
        Mock Get-ScheduledTask { }
        Mock New-LocalUser { }
        Mock Add-LocalGroupMember { }
        Mock Read-Host { ConvertTo-SecureString 'MockOnly-NotAnAccountPassword' -AsPlainText -Force }
        Mock cmd.exe { $global:LASTEXITCODE = 2 }
        Mock schtasks.exe { $global:LASTEXITCODE = 0 }
        Mock auditpol.exe { $global:LASTEXITCODE = 0 }
    }

    It 'previews by default without prompting or changing the host' {
        & $Harness | Should -Match '^Preview:'
        Should -Invoke Read-Host -Times 0 -Exactly
        Should -Invoke New-LocalUser -Times 0 -Exactly
        Should -Invoke Add-LocalGroupMember -Times 0 -Exactly
        Should -Invoke cmd.exe -Times 0 -Exactly
        Should -Invoke schtasks.exe -Times 0 -Exactly
        Should -Invoke auditpol.exe -Times 0 -Exactly
    }

    It 'makes no changes under Commit WhatIf' {
        & $Harness -Commit -WhatIf
        Should -Invoke Read-Host -Times 0 -Exactly
        Should -Invoke New-LocalUser -Times 0 -Exactly
        Should -Invoke Add-LocalGroupMember -Times 0 -Exactly
        Should -Invoke cmd.exe -Times 0 -Exactly
        Should -Invoke schtasks.exe -Times 0 -Exactly
        Should -Invoke auditpol.exe -Times 0 -Exactly
    }

    It 'refuses an existing user before any mutation' {
        Mock Get-LocalUser { [pscustomobject]@{ Name = 'lab03_user' } }
        { & $Harness -Commit } | Should -Throw '*already exists*'
        Should -Invoke Read-Host -Times 0 -Exactly
        Should -Invoke cmd.exe -Times 0 -Exactly
        Should -Invoke New-LocalUser -Times 0 -Exactly
    }

    It 'refuses an existing task before creating an account' {
        Mock Get-ScheduledTask { [pscustomobject]@{ TaskPath = '\Lab03\'; TaskName = 'CanaryTask' } }
        { & $Harness -Commit } | Should -Throw '*already exists*'
        Should -Invoke New-LocalUser -Times 0 -Exactly
        Should -Invoke schtasks.exe -Times 0 -Exactly
    }

    It 'creates a disabled account with a secure password in the mocked commit path' {
        & $Harness -Commit | Should -Match 'Lab actions completed'
        Should -Invoke New-LocalUser -Times 1 -Exactly -ParameterFilter {
            $Name -eq 'lab03_user' -and $Disabled -and $Password -is [securestring]
        }
        Should -Invoke Add-LocalGroupMember -Times 1 -Exactly -ParameterFilter { $SID -eq 'S-1-5-32-544' }
        Should -Invoke auditpol.exe -Times 1 -Exactly
    }

    It 'stops after a task failure and reports that earlier changes may remain' {
        Mock schtasks.exe { $global:LASTEXITCODE = 1 }
        { & $Harness -Commit } | Should -Throw '*Earlier changes may remain*Scheduled task creation failed*'
        Should -Invoke New-LocalUser -Times 1 -Exactly
        Should -Invoke auditpol.exe -Times 0 -Exactly
    }
}
