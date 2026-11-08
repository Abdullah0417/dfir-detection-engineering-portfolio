# Executive Summary — Controls-to-Telemetry Audit

## Objective
Assess whether critical endpoint controls are **observable** via telemetry in Microsoft Sentinel and deliver a repeatable **validation harness** (known-good events + pass/fail KQL).

## High-level findings (from validation + dashboard screenshots)
**Strengths (observable telemetry present):**
- Agent health and ingestion validated via `Heartbeat` + `Event`.
- Sysmon process creation (EID 1) observed on both endpoints in the captured lookback window.
- Authentication telemetry (4624/4625) observed on both endpoints in the captured lookback window.
- Scheduled task creation (4698) and privileged logon sessions (4672) observed on both endpoints in the captured lookback window.

**Gaps / partial coverage (fleet-level):**
- Sysmon network connection telemetry (EID 3) was observed on `win-ws1` but not on `win-ws2` in the captured lookback window.
- Audit policy tampering (4719) was observed on `win-ws1`; fleet-level coverage depends on generating/validating equivalent activity across endpoints.
- Security log cleared (1102) was not tested (destructive) — included as an optional control.

## Detection & response uplift delivered
- **Scheduled analytic rule (ARM export):** `LAB03 - Audit/Log Tampering (4719/1102)`
- **SOAR-lite automation (ARM export):** tag + severity standardization on incident creation
- **Workbook dashboard:** stakeholder KPIs + technical drill-down

## Risk impact (why this matters)
Missing telemetry limits investigation. An absent event can reflect missing test activity, a collection gap, or the chosen time window; those causes need separate checks.

## Recommendations (prioritized)
1) **High:** Validate required signals on **every endpoint** (run the canary harness per host) and track gaps using the matrix.
2) **High:** Ensure Sysmon network telemetry (EID 3) is consistently observed across endpoints (config + activity generation + DCR ingest).
3) **Medium:** Add a high-signal alert for local Administrators group membership changes (4732) if this is a key risk.
4) **Low (lab-only):** Test 1102 in a disposable environment and ensure the tampering detection triggers as expected.
