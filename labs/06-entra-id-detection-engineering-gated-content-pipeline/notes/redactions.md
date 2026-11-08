# Redaction log

## Purpose

This file records what I reviewed before publishing Lab 06 and what I chose to redact, keep, or leave local.

## Files reviewed

- [Failed sign-in burst analytic export](../detections/exports/analytics/rule_failed_signin_burst.json)
- [Directory role assignment change analytic export](../detections/exports/analytics/rule_role_assignment_change.json)
- [Service principal credential addition analytic export](../detections/exports/analytics/rule_sp_credential_addition.json)
- [Identity triage automation export](../automation/exports/identity-triage-automation.export.json)
- [Identity dashboard workbook export](../workbooks/exports/identity_dashboard.json)
- [Deployable workbook wrapper](../pipeline/deploy/workbook.serialized.json)
- supporting markdown notes used to explain the lab

## What I redacted in the public write-up

- the public source IP used during sign-in testing
- exact actor identities where a role label or generic description was enough
- full tenant-specific UPN values where a placeholder or sanitized alias was enough
- correlation identifiers that were only needed during validation
- exact app, object, and service principal IDs from the OIDC setup notes
- full subscription-scope resource IDs from the public OIDC notes

## What I intentionally kept

- rule names and detection descriptions
- `OperationName` values needed to explain the detection logic
- rule schedules, thresholds, and entity mappings
- workbook section names and the query logic needed to explain the analyst view
- scenario timestamps and sequence details needed to explain the validation flow
- the GitHub org, repo name, and environment name because they are part of the public repo story

## Current source exclusions

- Local OIDC values, raw workflow outputs under `artifacts/`, and generated packages under `dist/` are excluded from source control.
- Previously tracked runtime outputs were removed during review. Existing Git history is unchanged.
- The identity workbook now uses `<SUBSCRIPTION_ID>` for subscription references. Replace it when adapting the workbook to your lab.
- The identity observable list uses `<SOURCE_IP>` instead of the original source subnet.

These changes reduce environment details in the current source. They do not remove values from historical commits or earlier workflow logs.
