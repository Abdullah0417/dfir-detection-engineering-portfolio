# Executive Summary — (Endpoint Forensics Casework)

## Controlled test activity
- A PowerShell script was dropped into %APPDATA%\AdobeUpdate\adobeupdate.ps1 and executed on win-ws1.
- A scheduled task (AdobeUpdateSvc) was created to persist execution at user logon, launching PowerShell with bypass-style flags.

## Impact (lab framing)
- Demonstrates how a common persistence pattern can be validated using disk artifacts (MFT) and Windows event logs (EVTX).
- Converts investigation findings into detection engineering in Microsoft Sentinel (hunt queries, analytic rule, incident, automation rule, and workbook).

## Evidence sources
- $MFT (KAPE triage collection) → MFTECmd parsing (local only)
- Windows EVTX exports (Security/System/Application/Sysmon) → EvtxECmd parsing (local only)
- Microsoft Sentinel logs (KQL hunts + analytic rule)

## Actions taken
- Collected triage artifacts and generated a SHA256 evidence manifest.
- Correlated file system + event telemetry into a UTC timeline.
- Published a small IOC pack (publish-safe) derived from validated evidence.
- Created Sentinel content: hunts, analytic rule, incident proof, automation rule, and workbook.

## Recommendations
- Alert on PowerShell launched from user profile paths with suspicious flags (e.g., -ExecutionPolicy Bypass, -WindowStyle Hidden) and script execution from %APPDATA%.
- Baseline scheduled tasks per host; alert on newly created tasks, especially those running with elevated privileges or executing from user-writable locations.
- Ensure Sysmon process creation telemetry is consistently ingested and normalized for reliable command-line detection.
