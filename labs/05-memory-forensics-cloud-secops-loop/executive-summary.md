# Executive summary — (Memory forensics + Sentinel SecOps loop)

## Summary
I investigated repeated PowerShell executions using `-EncodedCommand` on an Azure VM (`win-ws1`) and converted that investigation into an operational Sentinel workflow:
- Hunts that **decode the payload**
- A scheduled analytic rule that alerts on encoded-command candidates and attempts to decode the canary
- An automation rule that tags incidents (`lab05`) and escalates severity
- A “case view” workbook for fast triage

Because full-RAM Volatility triage was not reliable in the Azure guest environment, the memory component pivots to **process-memory evidence** (PowerShell process dump + strings proof).

## Why this mattered
Encoded PowerShell is a common tradecraft pattern for:
- hiding intent from basic logging
- staging multi-line scripts without dropping files

Decoding the command line helps inspect the test payload. Encoding alone does not establish malicious intent.

## What I observed
- Sysmon EID 1 showed `powershell.exe` launched with `-EncodedCommand` on `win-ws1`.
- The decoded payload contained deterministic markers (`LAB05_CANARY_START`) and a benign outbound web request (lab canary).
- Process-memory strings from the PowerShell dump contained the same markers and the full encoded command line.

## What I built (deliverables)
- **Hunts (KQL):**
  - Baseline EID 1 EncodedCommand
  - Decoded payload extraction
  - EID 1 ↔ EID 3 correlation by ProcessGuid
- **Detection:** scheduled analytic rule exported as JSON (rules-as-code)
- **Automation:** incident tag + severity escalation exported as JSON
- **Workbook:** parameterized “case view” exported as JSON
- **Evidence pack:** hash-only manifest, chain-of-custody, IOC pack, proof screenshots

## Key constraints and decision
- Full-RAM images acquired inside Azure repeatedly failed Volatility kernel discovery (`pdbscan` / missing `kernel.layer_name`).
- To stay Azure-only and still produce memory-backed proof, I pivoted to **process-memory forensics**.

(Details: `notes/pivot-constraints-and-decision.md`)

## Recommendations (if this were production)
- Keep the detection, but tune it:
  - allowlist known automation tooling
  - add additional context requirements (parent process, user, decoded keyword hits)
- Add response actions:
  - enrich incident with decoded payload snippet
  - optionally isolate host / disable account (depends on environment)
- Consider adding identity and cloud posture signals (Entra ID, Defender for Cloud) if licensing and cost allow.

## Proof / evidence pointers
- Workbook view: `screenshots/00_workbook_case_view.png`
- Incident automation proof: `screenshots/01_incident_tagged_high_lab05.png`
- Memory strings proof: `screenshots/08_strings_hits_canary_markers.png`, `screenshots/09_strings_hits_encoded_commandline.png`
- Rule exports: `detections/`, `automation/`, `workbooks/`

