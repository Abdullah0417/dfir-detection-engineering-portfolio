# Multi-host Incident Reconstruction (Microsoft Sentinel + Sysmon)

**Quick links:** [Timeline KQL](kql/lab02_timeline.kql) · [Analytic rule export](detections/LAB02_encoded_powershell_rule.arm.json) · [Automation export](automation/LAB02_soar_lite_automation_rule.arm.json) · [Workbook template](workbooks/LAB02_timeline_dashboard.galleryTemplate.json) · [Executive summary](executive-summary.md)

## What I tested

- Multi-host endpoint telemetry ingestion into Sentinel (`win-ws1`, `win-ws2`) validated via `Heartbeat` and Windows Event Logs.
- Cross-host reconstruction using a single **timeline query** that correlates Sysmon + Security events.
- Hunt → **Scheduled analytic rule** shipped: `LAB02 - Encoded PowerShell Execution` (MITRE `T1059.001`).
- **SOAR-lite automation** shipped: tag + severity escalation on incident creation.
- **Workbook dashboard** for reviewing the timeline.

## Topology (lab)

- `win-ws1` — Windows endpoint
- `win-ws2` — Windows endpoint
- `ub-attacker` — Ubuntu attacker VM (optional; internal only, not onboarded to Sentinel for this lab)
- Log Analytics workspace: `law-dfir`
- Resource group: `rg-dfir-lab-scus`

## Data sources / tables used

- `Heartbeat` — agent health
- `Event` — Windows Event Logs via AMA + DCR
- Sysmon: `Microsoft-Windows-Sysmon/Operational` (EIDs: `1`, `3`)
- Security: `Security` (EIDs: `4624`, `4625`)

**Implementation detail:** in this workspace, `Event.EventData` is XML (string).  
Queries parse it using `parse_xml()` and build a bag to extract fields like `Image`, `CommandLine`, and account names.

---

## Artifacts (this repo)

- Executive summary: [executive-summary.md](executive-summary.md)
- KQL queries: [kql/](kql/)
- Analytic rule export (ARM): [detections/LAB02_encoded_powershell_rule.arm.json](detections/LAB02_encoded_powershell_rule.arm.json)
- Automation rule export (ARM): [automation/LAB02_soar_lite_automation_rule.arm.json](automation/LAB02_soar_lite_automation_rule.arm.json)
- Workbook template: [workbooks/LAB02_timeline_dashboard.galleryTemplate.json](workbooks/LAB02_timeline_dashboard.galleryTemplate.json)
- IOC list (lab-scoped): [ioc/ioc_list.csv](ioc/ioc_list.csv)
- MITRE mapping: [mitre/mitre_mapping.md](mitre/mitre_mapping.md)
- Redactions note: [notes/redactions.md](notes/redactions.md)

---

## Import / Deploy (Portal)

This lab includes templates to adapt to your workspace:
- Analytic rule (ARM): [detections/LAB02_encoded_powershell_rule.arm.json](detections/LAB02_encoded_powershell_rule.arm.json)
- Automation rule (ARM): [automation/LAB02_soar_lite_automation_rule.arm.json](automation/LAB02_soar_lite_automation_rule.arm.json)
- Workbook template: [workbooks/LAB02_timeline_dashboard.galleryTemplate.json](workbooks/LAB02_timeline_dashboard.galleryTemplate.json)

> Prereqs: Microsoft Sentinel enabled on the workspace, and you have **Contributor** (or higher) on the resource group + workspace.

### A) Import the Analytic Rule (ARM)

1. Azure Portal → **Microsoft Sentinel**
2. Select your workspace (example: `law-dfir`)
3. Left menu → **Analytics**
4. Confirm the rule is not already present (search: `LAB02 - Encoded PowerShell Execution`)
5. Open a new tab: Azure Portal → **Deploy a custom template** (search the portal for “Deploy a custom template”)
6. Click **Build your own template in the editor**
7. Click **Load file** → upload:  
   - [detections/LAB02_encoded_powershell_rule.arm.json](detections/LAB02_encoded_powershell_rule.arm.json)
8. Click **Save**
9. Choose:
   - **Subscription**: your lab subscription
   - **Resource group**: `rg-dfir-lab-scus`
10. Click **Review + create** → **Create**
11. Back in Sentinel → **Analytics** → verify the rule exists and is **Enabled**.

### B) Import the Automation Rule (ARM)

1. Azure Portal → **Deploy a custom template**
2. Click **Build your own template in the editor**
3. Click **Load file** → upload:
   - [automation/LAB02_soar_lite_automation_rule.arm.json](automation/LAB02_soar_lite_automation_rule.arm.json)
4. Click **Save**
5. Select the same **Subscription** + **Resource group**
6. Click **Review + create** → **Create**
7. Sentinel → **Automation**
8. Verify the rule exists and is **Enabled**.

> Publish-safe note: this export does not assign an owner to avoid leaking user identifiers.

### C) Import the Workbook Template

1. Azure Portal → **Microsoft Sentinel**
2. Select workspace
3. Left menu → **Workbooks**
4. Click **+ Add workbook**
5. Click **Edit**
6. Click the **</> (Advanced editor)** button
7. Replace the JSON with the contents of:
   - [workbooks/LAB02_timeline_dashboard.galleryTemplate.json](workbooks/LAB02_timeline_dashboard.galleryTemplate.json)
8. Click **Apply**
9. Click **Save** (name it: `LAB02 - Timeline Dashboard`)

### D) Quick validation after import

- Sentinel → **Analytics**: rule `LAB02 - Encoded PowerShell Execution` is present + enabled
- Sentinel → **Automation**: automation rule is present + enabled
- Sentinel → **Workbooks**: `LAB02 - Timeline Dashboard` opens and renders

---

## Evidence (screenshots)

- Workbook dashboard: [`screenshots/workbook_timeline_dashboard.png`](screenshots/workbook_timeline_dashboard.png)
- Timeline results: [`screenshots/lab02_timeline_results.png`](screenshots/lab02_timeline_results.png)
- Events-by-host chart: [`screenshots/events_by_host_timechart.png`](screenshots/events_by_host_timechart.png)
- MITRE mapping view: [`screenshots/mitre_mapping_t1059_001.png`](screenshots/mitre_mapping_t1059_001.png)
- Incident automation: [`screenshots/incident_automation_applied.png`](screenshots/incident_automation_applied.png)
- Ub-attacker overview: [`screenshots/ub-attackers(ubuntu)_vm_overview.png`](screenshots/ub-attackers(ubuntu)_vm_overview.png)

---

## KQL queries (saved under kql/)

Ingestion validation:

- [`kql/01_heartbeat_agent_health.kql`](kql/01_heartbeat_agent_health.kql)
- [`kql/02_sysmon_event_counts_1h.kql`](kql/02_sysmon_event_counts_1h.kql)
- [`kql/03_security_logon_4624_4625_counts_1h.kql`](kql/03_security_logon_4624_4625_counts_1h.kql)

Investigation / reconstruction:

- [`kql/lab02_timeline.kql`](kql/lab02_timeline.kql)
- [`kql/04_events_by_host_5m_24h.kql`](kql/04_events_by_host_5m_24h.kql)

---

## Detection and automation

### Scheduled analytic rule

- Export: [`detections/LAB02_encoded_powershell_rule.arm.json`](detections/LAB02_encoded_powershell_rule.arm.json)
- Tuning notes: [`detections/tuning_notes.md`](detections/tuning_notes.md)

Behavior:

- Detects Sysmon EID 1 where PowerShell runs with `-EncodedCommand` / `-enc`.
- Frequency: every 5 minutes
- Lookback: 1 hour
- Event grouping: alert per result

### Automation rule (SOAR-lite)

- Export: [`automation/LAB02_soar_lite_automation_rule.arm.json`](automation/LAB02_soar_lite_automation_rule.arm.json)
- Notes: [`automation/README.md`](automation/README.md)

Behavior:

- Trigger: incident created from the LAB02 analytic rule
- Actions: tag `lab02`, set severity `High`

> Publish-safe note: owner assignment was removed to avoid leaking user identifiers. See [notes/redactions.md](notes/redactions.md).

---

## Workbook

- Template: [`workbooks/LAB02_timeline_dashboard.galleryTemplate.json`](workbooks/LAB02_timeline_dashboard.galleryTemplate.json)

Contents:

- Scenario text block
- Timeline grid (Sysmon + Security merged)
- Time chart (events-by-host, 5m bins)

---

## Repro steps (lab-safe)

### 1) Validate ingestion

Run the 3 ingestion KQL queries (`kql/01_*` → `kql/03_*`).

### 2) Generate a known-good signal (Encoded PowerShell)

Run on **either** `win-ws1` or `win-ws2`:

```powershell
$cmd = '"LAB02 encoded test $(Get-Date -Format o)" | Out-File C:\ProgramData\lab02_encoded_test.txt -Append'
$b64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
powershell.exe -NoProfile -EncodedCommand $b64
```
