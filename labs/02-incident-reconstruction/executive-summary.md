# Executive Summary (Incident Reconstruction)

## What happened
Two Windows hosts (`win-ws1`, `win-ws2`) generated endpoint telemetry into Microsoft Sentinel via AMA + DCR. Ingestion health was validated with `Heartbeat`, and Windows Event Logs were queried from the `Event` table.

A controlled test of **encoded PowerShell** execution was performed to create a realistic “obfuscated command execution” signal (Sysmon EID 1). Investigation correlated Sysmon process/network activity (EIDs 1 and 3) with Security logon activity (4624/4625) across both endpoints into a single timeline view.

## Impact (lab scope)
This activity was lab-generated and constrained to the DFIR lab environment. The objective was to demonstrate a lab investigation workflow: **ingest → validate → hunt → detect → automate response → present findings**.

## Actions taken
- **Timeline reconstruction:** built a multi-host timeline query (Sysmon + Security) and parsed XML `EventData` into consistent fields (account, image, command line).
- **Detection:** promoted the hunt into a scheduled analytic rule (`LAB02 - Encoded PowerShell Execution`) mapped to **MITRE ATT&CK T1059.001 (PowerShell)**.
- **Automation (SOAR-lite):** implemented an automation rule that tags the incident (`lab02`) and escalates severity to **High** on incident creation.
- **Reporting:** created a workbook (“LAB02 Timeline Dashboard”) for an investigation view.

## Recommendations
- Tune encoded PowerShell detection with environment-specific allowlists (parent process, known management tooling) and/or require additional context (e.g., suspicious parent, follow-on network activity).
- Add adjacent detections for persistence (scheduled tasks, services, Run keys) and correlate with network telemetry for faster triage.
- Keep published exports sanitized (remove subscription IDs, user identifiers). See `notes/redactions.md`.
