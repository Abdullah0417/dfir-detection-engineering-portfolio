# Service principal credential addition

## Purpose

Find service principal audit events that may indicate a credential change.

## Telemetry

- Table: `AuditLogs`
- Required fields:
  - `TimeGenerated`
  - `OperationName`
  - `InitiatedBy`
  - `TargetResources`
  - `ResultType`
  - `CorrelationId`
  - `LoggedByService`

## Logic

The rule looks back one hour for `Add service principal credentials` and `Update service principal`. It expands `TargetResources` so the alert includes the target application or service principal. `Update service principal` also covers unrelated changes; inspect modified properties and the result before concluding that a credential was added.

## Thresholds

- Trigger when query result count is greater than 0
- Lookback: 1 hour
- Run frequency: 1 hour

## Entity mapping

- Account:
  - `Name` -> `ActorName`
  - `UPNSuffix` -> `ActorUPNSuffix`

## Observed operation names used

- `Add service principal credentials`
- `Update service principal`

## False positives

- Legitimate secret rotation
- Planned application maintenance
- Test app bootstrap activity

## Validation

1. Add a password credential to the dedicated scenario service principal by using `az ad sp credential reset --append`.
2. Run the discovery hunt and capture the exact operation names.
3. Create the scheduled analytic.
4. Add a second temporary credential or repeat the event.
5. Confirm an incident is created.

## Limitations

The scenario used a dedicated lab service principal, but the query has no target-ID filter and searches all matching events in the workspace. It includes failed operations and does not distinguish credential addition from removal or other updates. Treat results as triage candidates. The OIDC deployment identity was separate from the scenario identity.

## Evidence

- [Service principal credential-addition hunt result](../../screenshots/07_sp_credential_addition_hunt.png)
- [Scheduled analytic configuration](../../screenshots/10_rule_sp_credential_addition.png)
- [Incident triggered from the rule](../../screenshots/11_identity_incident_triggered.png)
