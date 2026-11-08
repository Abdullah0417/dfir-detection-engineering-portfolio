# Response Workflow — Security Hub to EventBridge to Lambda

## Purpose
This workflow updates GuardDuty findings in Security Hub for triage. It sets status and adds a note; it does not contain or remediate the affected resource.

## Trigger
- Security Hub imported findings event
- Product: GuardDuty
- Workflow status: `NEW`
- Record state: `ACTIVE`
- Severity: `HIGH` or `CRITICAL`

## Event pattern artifact
- `eventbridge_securityhub_guardduty_new_high_to_lambda.json`

## Target
- Lambda function

## Lambda action
The Lambda function calls `BatchUpdateFindings` to:
- set `Workflow.Status` to `NOTIFIED`
- add a note that records the automated response

Code artifact:
- `lambda_handler.py`

## Constraint, decision, and evidence
Security Hub was enabled after the first sample-finding batch. Because of that timing, the response workflow was validated against a second batch generated after Security Hub was already importing findings.

One finding was also updated manually by CLI so the final `NOTIFIED` state was easy to show in the Security Hub console. The console screenshot alone cannot attribute the final state to Lambda.

## Validation evidence
- `../../screenshots/06_response_executed.png`
- Lambda CloudWatch logs showing successful `workflow_status = NOTIFIED`

## Why `NOTIFIED` was the right response here
The lab uses sample findings. `NOTIFIED` records a triage workflow state; it does not confirm containment or remediation.

## Operational note
The original logs showed at least one `TooManyRequestsException` from the Security Hub API during burst processing. The handler now raises on API exceptions and rejected updates so the invocation fails and can use Lambda retry handling. It logs `NOTIFIED` only after an accepted update. Retry exhaustion and delivery guarantees have not been tested live.
