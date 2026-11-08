# Redactions

Goal: keep the repo **publish-safe** while still being **reproducible**.

## What gets redacted
### 1) Sentinel exports (ARM templates)
Files:
- `detections/LAB03_audit_log_tampering_rule.arm.json`
- `automation/LAB03_soar_lite_automation_rule.arm.json`

Redaction pattern:
- Replace exported GUIDs in `resources[].id` and `resources[].name` with:
  - `00000000-0000-0000-0000-000000000000`

See per-artifact notes:
- `detections/redactions.md`
- `automation/redactions.md`

### 2) Workbook exports (galleryTemplate)
File:
- `workbooks/LAB03_telemetry_coverage_dashboard.galleryTemplate.json`

Redaction pattern:
- Replace Azure identifiers with placeholders:
  - `/subscriptions/<SUBSCRIPTION_ID>/resourcegroups/<RESOURCE_GROUP>/.../workspaces/<WORKSPACE_NAME>`

See:
- `workbooks/redactions.md`

## Quick pre-commit scan
Search for anything that looks like an Azure identifier or identity:
- `subscriptions/`
- `resourcegroups/`
- `tenant`
- `objectId` / `principalId`
- email-like strings (`@`)

## What is safe to leave in
- Lab hostnames (`win-ws1`, `win-ws2`)
- KQL logic, event IDs, table names
- Canary identifiers listed in `ioc/canary_identifiers.md`

## Harness credential review

The original harness and its output screenshot contained a fixed lab-account password. The current screenshot masks only the password value; all other pixels match the original. The script now prompts for a password and previews changes by default. The original lab environment has been deleted. Historical commits still contain the old password; this review does not rewrite history.
