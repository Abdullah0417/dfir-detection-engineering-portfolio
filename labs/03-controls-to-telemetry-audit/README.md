# Controls-to-Telemetry Audit (Microsoft Sentinel)

**Quick links:**
- **Workbook (dashboard):** [`workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json`](workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json)
- **Telemetry coverage matrix:** [`notes/telemetry_coverage_matrix.md`](notes/telemetry_coverage_matrix.md) · [`notes/telemetry_coverage_matrix.csv`](notes/telemetry_coverage_matrix.csv)
- **Validation KQL pack (pass/fail):** [`kql/validation/`](kql/validation/)
- **Workbook KQL (executive + drill-down):** [`kql/workbook/`](kql/workbook/)
- **Analytic rule export (ARM):** [`detections/LAB03_audit_log_tampering_rule.arm.json`](detections/LAB03_audit_log_tampering_rule.arm.json)
- **Automation rule export (ARM):** [`automation/LAB03_soar_lite_automation_rule.arm.json`](automation/LAB03_soar_lite_automation_rule.arm.json)
- **Executive summary:** [`executive-summary.md`](executive-summary.md)

---

![LAB03 — Telemetry Coverage Dashboard](screenshots/16_workbook_overview.png)

## What I tested
- Generated known test events and checked which appeared in Sentinel.
- Compared results across two Windows endpoints using a coverage matrix and workbook.
- Created an audit/log-tampering rule with incident tagging and ATT&CK mappings.

The score counts observed event types in the selected window. It does not measure overall security effectiveness.

## Scenario & scope
Exercise: Windows telemetry coverage check
Environment: Azure lab (2 Windows endpoints) → Microsoft Sentinel (Log Analytics)  
Primary question: **“If something bad happens, will we see it — and can we prove it?”**

**In scope (endpoint controls → telemetry):**
- Authentication: successful + failed logons
- Privileged sessions
- Account + group management (local admin group changes)
- Scheduled task persistence
- Audit/log tampering signals
- Sysmon process + network visibility

**Out of scope:**
- Defender for Endpoint deep integration
- Full SOAR playbooks with external connectors
- Domain Controller telemetry (no DC in this lab)

## Topology (lab)
- `win-ws1` — Windows endpoint
- `win-ws2` — Windows endpoint
- Log Analytics workspace: `law-dfir`

## Data sources / tables used
- `Heartbeat` — agent health / last seen
- `Event` — Windows Event Logs via AMA + DCR
  - Sysmon: `Microsoft-Windows-Sysmon/Operational` (EIDs: 1, 3)
  - Security: `Security` (auth + admin activity)

Implementation detail: in this workspace, `Event.EventData` is XML (string). Queries parse it using `parse_xml()` and build a bag to extract fields.

## Artifacts (this repo)
- **Executive summary:** [`executive-summary.md`](executive-summary.md)
- **Coverage matrix (MD + CSV):** [`notes/telemetry_coverage_matrix.md`](notes/telemetry_coverage_matrix.md) · [`notes/telemetry_coverage_matrix.csv`](notes/telemetry_coverage_matrix.csv)
- **Control test harness:** [`notes/control_test_harness.md`](notes/control_test_harness.md) · [`notes/control_test_harness_winws1.ps1`](notes/control_test_harness_winws1.ps1)
- **Validation KQL:** [`kql/validation/`](kql/validation/)
- **Workbook KQL:** [`kql/workbook/`](kql/workbook/)
- **Detection shipped (KQL):** [`detections/audit_log_tampering.kql`](detections/audit_log_tampering.kql)
- **Analytic rule export (ARM):** [`detections/LAB03_audit_log_tampering_rule.arm.json`](detections/LAB03_audit_log_tampering_rule.arm.json)
- **Automation rule export (ARM):** [`automation/LAB03_soar_lite_automation_rule.arm.json`](automation/LAB03_soar_lite_automation_rule.arm.json)
- **Workbook export (galleryTemplate):** [`workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json`](workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json)
- **MITRE mapping:** [`mitre/mitre_mapping.md`](mitre/mitre_mapping.md)
- **Canary identifiers:** [`ioc/canary_identifiers.md`](ioc/canary_identifiers.md)
- **Screenshots (evidence):** [`screenshots/`](screenshots/)
- **Redactions notes:** [`notes/redactions.md`](notes/redactions.md)

---

## Import / deploy (Portal)
This lab includes templates to adapt to your workspace.

**Prereqs**
- Microsoft Sentinel enabled on the workspace
- Contributor (or higher) on the resource group + workspace

### A) Import the Analytic Rule (ARM)
1. Azure Portal → **Microsoft Sentinel** → select your workspace (example: `law-dfir`)
2. **Analytics** → confirm the rule is not already present (search: `LAB03 - Audit/Log Tampering`)
3. Azure Portal → **Deploy a custom template**
4. **Build your own template in the editor** → **Load file**:
   - [`detections/LAB03_audit_log_tampering_rule.arm.json`](detections/LAB03_audit_log_tampering_rule.arm.json)
5. **Save** → choose your Subscription + Resource Group → **Review + create** → **Create**
6. Back in Sentinel → **Analytics** → verify the rule exists and is **Enabled**

### B) Import the Automation Rule (ARM)
1. Azure Portal → **Deploy a custom template** → **Build your own template in the editor**
2. **Load file**:
   - [`automation/LAB03_soar_lite_automation_rule.arm.json`](automation/LAB03_soar_lite_automation_rule.arm.json)
3. **Save** → same Subscription + Resource Group → **Review + create** → **Create**
4. Sentinel → **Automation** → verify the rule exists and is **Enabled**

### C) Import the Workbook (galleryTemplate)
1. Sentinel → **Workbooks** → **+ Add workbook**
2. **Edit** → `</>` (**Advanced editor**)
3. Replace JSON with:
   - [`workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json`](workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json)
4. **Apply** → **Save** as: `LAB03 — Telemetry Coverage Dashboard`

---

## Repro / validation (lab-safe)
### 1) Generate known-good signals (canary harness)
- Follow: [`notes/control_test_harness.md`](notes/control_test_harness.md)
- Script option (run on `win-ws1`): [`notes/control_test_harness_winws1.ps1`](notes/control_test_harness_winws1.ps1)

The harness previews changes by default. Use `-Commit -WhatIf` to inspect the plan and `-Commit` to apply it on an elevated, disposable lab VM. It prompts for a password, creates a disabled canary account with local Administrators membership, creates a task, and changes audit policy. Restore the VM snapshot after testing. Run equivalent tests on each host before comparing coverage.

### 2) Run validation KQL (pass/fail)
Run the queries in order:
- [`kql/validation/00_inventory_hosts_seen.kql`](kql/validation/00_inventory_hosts_seen.kql)
- [`kql/validation/01_heartbeat_agent_health.kql`](kql/validation/01_heartbeat_agent_health.kql)
- Sysmon coverage: `02_*` and `03_*`
- Security coverage: `04_*` through `12_*`

### 3) Confirm workbook renders (executive + technical)
- Executive section (stakeholder-friendly KPIs): coverage score, endpoints reporting, top gaps, trends
- Technical section: raw validation drill-down

### 4) Fill the coverage matrix
Update:
- [`notes/telemetry_coverage_matrix.md`](notes/telemetry_coverage_matrix.md)
- [`notes/telemetry_coverage_matrix.csv`](notes/telemetry_coverage_matrix.csv)

---

## Evidence (screenshots)
- Repo structure: [`screenshots/00_repo_structure.png`](screenshots/00_repo_structure.png)
- Heartbeat validation: [`screenshots/02_validation_heartbeat.png`](screenshots/02_validation_heartbeat.png)
- Sysmon validation: [`screenshots/03_validation_sysmon_eid1.png`](screenshots/03_validation_sysmon_eid1.png) · [`screenshots/04_validation_sysmon_eid3.png`](screenshots/04_validation_sysmon_eid3.png)
- Security validation: [`screenshots/05_validation_4624.png`](screenshots/05_validation_4624.png) · [`screenshots/06_validation_4625.png`](screenshots/06_validation_4625.png) · [`screenshots/07_validation_4732.png`](screenshots/07_validation_4732.png) · [`screenshots/08_validation_4698.png`](screenshots/08_validation_4698.png) · [`screenshots/09_validation_4719.png`](screenshots/09_validation_4719.png)
- Analytic rule: [`screenshots/12_analytic_rule_overview.png`](screenshots/12_analytic_rule_overview.png) · [`screenshots/11_analytic_rule_query.png`](screenshots/11_analytic_rule_query.png) · [`screenshots/10_analytic_rule_mitre_mapping.png`](screenshots/10_analytic_rule_mitre_mapping.png)
- Incident proof: [`screenshots/13_incident_triggered.png`](screenshots/13_incident_triggered.png) · [`screenshots/14_related_events_4719.png`](screenshots/14_related_events_4719.png)
- Automation proof: [`screenshots/15_automation_rule.png`](screenshots/15_automation_rule.png)
- Workbook overview: [`screenshots/16_workbook_overview.png`](screenshots/16_workbook_overview.png) · [`screenshots/16_workbook_overview_exec.png`](screenshots/16_workbook_overview_exec.png)

---

## Publish-safe note (redactions)
Before committing exports to GitHub:
- ARM templates: sanitize GUIDs in `resources[].id` and `resources[].name` (this repo uses `00000000-0000-0000-0000-000000000000`)
- Workbooks: replace Subscription / Resource Group / Workspace identifiers with placeholders

See: [`notes/redactions.md`](notes/redactions.md)
