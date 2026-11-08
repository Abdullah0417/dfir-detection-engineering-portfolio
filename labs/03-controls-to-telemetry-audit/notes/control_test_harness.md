# Control Test Harness (benign)

Generate known activity and check whether the expected audit events reach Sentinel. Audit policy, collection settings, and ingestion delay affect the results.

Run on a disposable Windows VM from an elevated, 64-bit PowerShell session. Take a VM snapshot first. The harness changes local account membership, creates a SYSTEM task, and updates audit policy.

```powershell
.\control_test_harness_winws1.ps1
.\control_test_harness_winws1.ps1 -Commit -WhatIf
.\control_test_harness_winws1.ps1 -Commit
```

The first two commands preview. `-Commit` prompts for a unique password and creates the account disabled. Existing accounts/tasks are refused. A failure stops later actions, but earlier changes can remain. After checking telemetry, restore the snapshot to remove the canary user/task and restore the original audit policy. No automatic cleanup is performed.

## Canary identifiers (safe to publish)
- Local test user: lab03_user
- Scheduled task name: \Lab03\CanaryTask

## Actions
A) Failed logon (4625)

B) Create a disabled local user (4720)

C) Add user to local Administrators (4732)

D) Create scheduled task (4698)

E) Modify audit policy (4719)

Optional (use with caution):
F) Clear Security log (1102) — destructive locally; do not do this outside a disposable lab
