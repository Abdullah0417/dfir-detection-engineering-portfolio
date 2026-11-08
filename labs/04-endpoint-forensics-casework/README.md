# Endpoint Forensics Casework (MFT + EVTX)

**Quick links:** [What I tested](#what-this-proves) · [Scenario & scope](#scenario-and-scope) · [Data sources](#data-sources-used) · [Workflow](#workflow) · [Key findings](#key-findings) · [Detections](#detections-shipped) · [Automation](#automation-shipped) · [Workbooks](#workbooks-shipped) · [MITRE](#mitre-mapping) · [IOCs](#iocs) · [Recommendations](#recommendations) · [Repro steps](#repro-steps) · [Artifacts index](#artifacts-index)

<a id="what-this-proves"></a>
## 1) What I tested
- I can run **endpoint triage** and preserve evidence boundaries ([hash manifest](notes/evidence_manifest.csv) + [chain-of-custody](notes/chain_of_custody.md); no raw artifacts published).
- I can **correlate disk artifacts (MFT)** with **Windows event telemetry (EVTX/Sentinel)** to build an incident [timeline](notes/timeline.md).
- I can translate forensic findings into **Sentinel detections**: hunts → [scheduled analytic rule](#detections-shipped) → [automation](#automation-shipped) → [workbook](#workbooks-shipped).
- I can produce a **publish-safe IOC pack** ([hashes + paths + persistence artifacts](ioc/malware_triage_iocs.csv)) without uploading samples.

<a id="scenario-and-scope"></a>
## 2) Scenario & scope
A controlled, benign “persistence-style” scenario was executed on a single Windows endpoint:

- **Host:** `win-ws1`
- **Time window (UTC):** 2026-02-24 22:45Z → 22:47Z
- **Activity simulated:**
  - A PowerShell script (`adobeupdate.ps1`) placed under a user-writable AppData path.
  - PowerShell executed the script with bypass-style flags.
  - A Scheduled Task (`AdobeUpdateSvc`) created for logon persistence.

**Scope boundary:** This repo contains only **documentation + screenshots + KQL + publish-safe templates + hash manifests**. Raw evidence (EVTX, `$MFT`, tool output directories, parsed CSVs) stays local. See also: [Notes (evidence discipline)](#notes-evidence-discipline) and [Artifacts index](#artifacts-index).

<a id="data-sources-used"></a>
## 3) Data sources used
| Source | Where | What it provided |
|---|---|---|
| `$MFT` | Local triage collection | File create timestamps + file path for `adobeupdate.ps1` |
| EVTX: Sysmon | Local export + Sentinel `Event` table | Process creation (Sysmon EID 1) for PowerShell execution |
| EVTX: Security | Local export + Sentinel `Event` table | Scheduled task creation (Security EID 4698) |
| Microsoft Sentinel | `Event` table (AMA + DCR) | Hunting + scheduled analytics + incident creation |

<a id="workflow"></a>
## 4) Workflow
1. **Collect** triage artifacts locally (KAPE `$MFT`, export EVTX with `wevtutil`).
2. **Hash + document** evidence ([manifest](notes/evidence_manifest.csv) + [chain-of-custody](notes/chain_of_custody.md)).
3. **Parse** artifacts locally (MFTECmd for MFT, EvtxECmd for EVTX).
4. **Identify suspicious artifacts** (AppData script path + suspicious PowerShell command line + scheduled task).
5. **Build a timeline** and cross-reference between MFT + EVTX ([full timeline](notes/timeline.md)).
6. **Hunt in Sentinel** using the [KQL hunts](#detections-shipped).
7. **Promote a hunt to a scheduled analytic rule** ([rules-as-code export](#detections-shipped)).
8. Add **SOAR-lite automation** ([section 7](#automation-shipped)) and a **workbook view** ([section 8](#workbooks-shipped)) for fast triage.
9. **Report**: [executive summary](executive-summary.md) + recommendations.

<a id="key-findings"></a>
## 5) Key findings
- **Suspicious script written to AppData Roaming** (`...\AppData\Roaming\AdobeUpdate\adobeupdate.ps1`).
  - Evidence: [screenshots/07_mft_suspicious_file_row.png](screenshots/07_mft_suspicious_file_row.png)
- **PowerShell executed the script with bypass-style flags**.
  - Evidence: [screenshots/09_evtx_powershell_exec_sysmon.png](screenshots/09_evtx_powershell_exec_sysmon.png)
- **Scheduled task created for logon persistence** (`AdobeUpdateSvc`).
  - Evidence: [screenshots/08_evtx_task_create_4698.png](screenshots/08_evtx_task_create_4698.png)
- **Sentinel hunts** returned matching events (process execution + task creation).
  - Evidence: [screenshots/11_sentinel_hunt_results.png](screenshots/11_sentinel_hunt_results.png)
  - Hunts used: [section 6](#detections-shipped)
- **Detection and incident handling:** scheduled analytic rule, incident creation, automation rule, and workbook.
  - Analytic rule proof: [screenshots/12_analytic_rule_mitre_mapping.png](screenshots/12_analytic_rule_mitre_mapping.png)
  - Incident proof: [screenshots/13_incident_triggered.png](screenshots/13_incident_triggered.png)
  - Automation proof (redacted): [screenshots/14_automation_rule.png](screenshots/14_automation_rule.png)
  - Workbook proof: [screenshots/15_workbook_overview.png](screenshots/15_workbook_overview.png)
  - Related sections: [Detections](#detections-shipped) · [Automation](#automation-shipped) · [Workbooks](#workbooks-shipped)

### Artifact → detection mapping (how the casework becomes Sentinel detections)
| Artifact finding | Hunt | Scheduled rule | Automation | Workbook |
|---|---|---|---|---|
| AppData script write (MFT) | N/A (disk artifact) | N/A | N/A | N/A |
| Security 4698 task created | [`kql/01_hunt_scheduled_task_4698.kql`](kql/01_hunt_scheduled_task_4698.kql) | (future hardening) correlate task action + PowerShell flags | Tag + severity | Panel: 4698 timechart |
| Sysmon EID 1 PowerShell exec | [`kql/02_hunt_powershell_exec_script_path.kql`](kql/02_hunt_powershell_exec_script_path.kql) | [`detections/LAB04_appdata_powershell_persistence_rule.arm.json`](detections/LAB04_appdata_powershell_persistence_rule.arm.json) | [`automation/LAB04_soar_lite_automation_rule.arm.json`](automation/LAB04_soar_lite_automation_rule.arm.json) | Panel: Sysmon EID 1 table + flag breakdown |

Full timeline (UTC): [notes/timeline.md](notes/timeline.md)

<a id="detections-shipped"></a>
## 6) Detections shipped
### Scheduled analytic rule
- **Name:** `LAB04 - PowerShell persistence-style script execution from AppData`
- **Scope:** the specific AdobeUpdate canary path; this is not a general detector for all AppData script execution.
- **Severity:** High
- **Schedule:** every 5 minutes over the last 1 hour
- **Entity mapping:** Host (`Computer` → `HostName`)
- **Rules-as-code:** [detections/LAB04_appdata_powershell_persistence_rule.arm.json](detections/LAB04_appdata_powershell_persistence_rule.arm.json)
- **Tuning notes:** [detections/tuning_notes.md](detections/tuning_notes.md)

### Hunts used to validate
- Scheduled task creation (Security 4698): [kql/01_hunt_scheduled_task_4698.kql](kql/01_hunt_scheduled_task_4698.kql)
- PowerShell execution (Sysmon EID 1): [kql/02_hunt_powershell_exec_script_path.kql](kql/02_hunt_powershell_exec_script_path.kql)

<a id="automation-shipped"></a>
## 7) Automation shipped
### SOAR-lite automation rule
- **Trigger:** when an incident is created and the title contains `LAB04`
- **Actions:**
  - Tag the incident: `lab04`
  - Escalate severity: `High`
- **Rules-as-code:** [automation/LAB04_soar_lite_automation_rule.arm.json](automation/LAB04_soar_lite_automation_rule.arm.json)
- **Proof (redacted):** [screenshots/14_automation_rule.png](screenshots/14_automation_rule.png)

<a id="workbooks-shipped"></a>
## 8) Workbooks shipped
### Workbook: “LAB04 - AppData PowerShell Persistence Overview”
- Shows:
  - Security 4698 scheduled task creation volume (timechart)
  - Sysmon EID 1 process executions referencing `adobeupdate.ps1`
  - A quick breakdown of suspicious PowerShell flags
- **Template:** [workbooks/LAB04_workbook_template.json](workbooks/LAB04_workbook_template.json)
- **Proof:** [screenshots/15_workbook_overview.png](screenshots/15_workbook_overview.png)

<a id="mitre-mapping"></a>
## 9) MITRE mapping
- T1059.001 — PowerShell
- T1053.005 — Scheduled Task

Details + evidence: [mitre/mitre_mapping.md](mitre/mitre_mapping.md)

<a id="iocs"></a>
## 10) IOCs
Publish-safe IOC pack (hashes + paths + task name — **no binaries**):
- [ioc/malware_triage_iocs.csv](ioc/malware_triage_iocs.csv)

<a id="recommendations"></a>
## 11) Recommendations
1. **Harden PowerShell**
   - Enable Script Block Logging and PowerShell Module Logging (where appropriate).
   - Alert on bypass-style flags (`-ExecutionPolicy Bypass`, `-EncodedCommand`, `-WindowStyle Hidden`).
2. **Scheduled task monitoring**
   - Add/expand detections on Security 4698 where task actions invoke PowerShell from user-writable paths.
3. **Endpoint controls**
   - Restrict user-write + execute patterns in `%APPDATA%` where feasible.
   - Investigate AppData script execution as a policy violation unless explicitly allowed.
4. **SOC workflow**
   - Use automation to tag/escalate and ensure consistent triage.
   - Keep a lightweight workbook to reduce time-to-context during incident review.

<a id="repro-steps"></a>
## 12) Repro steps
These steps are intended for a **controlled lab VM you own**.

1. Create a local case folder structure (do **not** store evidence inside the repo).
2. Generate benign activity that matches this scenario:
   - Place a harmless PowerShell script under `%APPDATA%\AdobeUpdate\` (e.g., write a timestamp to a log file).
   - Execute it using PowerShell with bypass-style flags.
   - Create a scheduled task that runs the script at logon.
3. Collect triage artifacts locally:
   - `$MFT` via KAPE
   - Export EVTX (Security + Sysmon) with `wevtutil epl`
4. Parse and correlate locally:
   - MFTECmd → identify the script write
   - EvtxECmd → identify Sysmon EID 1 and Security 4698
5. Validate in Sentinel:
   - Run the hunts in [kql/](kql/) and confirm they return the same events.
6. Deploy uplift artifacts:
   - Create the scheduled analytic rule using the query in [detections/](detections/).
   - Create the automation rule from [automation/](automation/).
   - Import the workbook template from [workbooks/](workbooks/).
7. Capture proof screenshots and update the [notes](notes/) files.

<a id="artifacts-index"></a>
## 13) Artifacts index
### Executive write-up
- [executive-summary.md](executive-summary.md)

### KQL
- [kql/01_hunt_scheduled_task_4698.kql](kql/01_hunt_scheduled_task_4698.kql)
- [kql/02_hunt_powershell_exec_script_path.kql](kql/02_hunt_powershell_exec_script_path.kql)

### Detections (rules-as-code)
- [detections/LAB04_appdata_powershell_persistence_rule.arm.json](detections/LAB04_appdata_powershell_persistence_rule.arm.json)
- [detections/tuning_notes.md](detections/tuning_notes.md)
- [detections/redactions.md](detections/redactions.md)

### Automation (rules-as-code)
- [automation/LAB04_soar_lite_automation_rule.arm.json](automation/LAB04_soar_lite_automation_rule.arm.json)
- [automation/redactions.md](automation/redactions.md)

### Workbooks
- [workbooks/LAB04_workbook_template.json](workbooks/LAB04_workbook_template.json)
- [workbooks/redactions.md](workbooks/redactions.md)

### MITRE
- [mitre/mitre_mapping.md](mitre/mitre_mapping.md)

<a id="notes-evidence-discipline"></a>
### Notes (evidence discipline)
- [notes/evidence_manifest.csv](notes/evidence_manifest.csv)
- [notes/chain_of_custody.md](notes/chain_of_custody.md)
- [notes/triage_checklist.md](notes/triage_checklist.md)
- [notes/timeline.md](notes/timeline.md)
- [notes/redactions.md](notes/redactions.md)

### Screenshots (proof)
- [screenshots/00_case_and_repo_structure.png](screenshots/00_case_and_repo_structure.png)
- [screenshots/01_case_structure.png](screenshots/01_case_structure.png)
- [screenshots/02_controlled_artifact_generation.png](screenshots/02_controlled_artifact_generation.png)
- [screenshots/03_kape_mft_collected.png](screenshots/03_kape_mft_collected.png)
- [screenshots/04_evtx_export_success.png](screenshots/04_evtx_export_success.png)
- [screenshots/05_evidence_manifest_preview.png](screenshots/05_evidence_manifest_preview.png)
- [screenshots/06_parsing_outputs_present.png](screenshots/06_parsing_outputs_present.png)
- [screenshots/07_mft_suspicious_file_row.png](screenshots/07_mft_suspicious_file_row.png)
- [screenshots/08_evtx_task_create_4698.png](screenshots/08_evtx_task_create_4698.png)
- [screenshots/09_evtx_powershell_exec_sysmon.png](screenshots/09_evtx_powershell_exec_sysmon.png)
- [screenshots/10_ioc_pack_preview.png](screenshots/10_ioc_pack_preview.png)
- [screenshots/11_sentinel_hunt_results.png](screenshots/11_sentinel_hunt_results.png)
- [screenshots/12_analytic_rule_mitre_mapping.png](screenshots/12_analytic_rule_mitre_mapping.png)
- [screenshots/13_incident_triggered.png](screenshots/13_incident_triggered.png)
- [screenshots/14_automation_rule.png](screenshots/14_automation_rule.png)
- [screenshots/15_workbook_overview.png](screenshots/15_workbook_overview.png)

[Back to top](#endpoint-forensics-casework-mft--evtx)
