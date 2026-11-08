# AWS GuardDuty Detection + Response

![Architecture diagram](screenshots/architecture_diagram.png)

## What I tested
- I built an AWS-native detection and response baseline with Terraform using GuardDuty, Security Hub, EventBridge, SNS, Lambda, S3, Athena, and KMS.
- I kept alerting and response as two separate workflows: GuardDuty to EventBridge to SNS for analyst notification, and Security Hub to EventBridge to Lambda for automated first response.
- I retained GuardDuty findings to S3, applied a lifecycle rule, and queried the exported dataset with Athena instead of relying on console-only visibility.
- I used Security Hub as the normalized ASFF finding layer for response logic and investigation pivots.
- I documented a real lab constraint honestly: Security Hub was enabled after the first sample-finding batch, so the Lambda response path was validated against the second batch, and one finding was manually updated by CLI to show `NOTIFIED` cleanly in the console.
- I packaged the lab as lab artifacts: screenshots, SQL queries, event patterns, Lambda code, Terraform, IOC details, and notes.

## Scenario and scope
This lab simulates an AWS-native SecOps workflow in a single AWS account and a single Region: `us-east-1`.

The environment was deployed with Terraform. GuardDuty sample findings were used as safe test data. The lab then proved five things in sequence:
1. GuardDuty generated findings.
2. Findings were exported to S3 for retention and queried with Athena.
3. High-severity GuardDuty events triggered an analyst-facing SNS email.
4. GuardDuty findings flowed into Security Hub in AWS Security Finding Format (ASFF).
5. Security Hub finding events triggered a Lambda response that updated workflow status to `NOTIFIED` by calling `BatchUpdateFindings`.

## Featured finding and why it was chosen
The strongest evidence chain in the uploaded artifacts centers on the GuardDuty sample finding below:

- **GuardDuty finding type:** `UnauthorizedAccess:EC2/TorClient`
- **MITRE ATT&CK mapping used in this package:** `T1090.003 – Multi-hop Proxy`


## Constraint, decision, and evidence
Security Hub was enabled after the first sample-finding batch. That timing mattered.

- **Constraint:** the first GuardDuty batch existed before Security Hub was ready to import and route those findings into the response workflow.
- **Decision:** generate a second sample-finding batch after Security Hub was enabled so EventBridge could invoke Lambda on Security Hub imported findings.
- **Evidence:** Lambda CloudWatch logs showed successful `workflow_status = NOTIFIED` updates for the second batch, and one finding was also updated manually by CLI so the final `NOTIFIED` state was easy to show in the Security Hub console.

The console screenshot shows the final state. By itself, it cannot establish whether Lambda or the manual CLI update produced that state.

## Architecture and data flow
The lab uses AWS-native services end to end:

- GuardDuty generates the finding.
- GuardDuty exports active findings to S3.
- Athena queries the S3 export for triage.
- GuardDuty also emits native events to EventBridge for the alert workflow.
- Security Hub imports GuardDuty findings in ASFF and emits finding events to EventBridge for the response workflow.
- Lambda updates the Security Hub finding workflow state to `NOTIFIED`.

## Core evidence chain
| Step | Artifact | What it proves |
|---|---|---|
| 1 | [`screenshots/01_finding_generated.png`](screenshots/01_finding_generated.png) | GuardDuty sample findings were generated in `us-east-1`. |
| 2 | [`screenshots/02_exported_to_s3.png`](screenshots/02_exported_to_s3.png) | GuardDuty exported findings to the S3 retention bucket. |
| 3 | [`screenshots/03_athena_query_result.png`](screenshots/03_athena_query_result.png) | Athena queried the exported findings successfully. |
| 4 | [`screenshots/04_eventbridge_rule_matched.png`](screenshots/04_eventbridge_rule_matched.png) | The EventBridge alert rule matched GuardDuty events and invoked its target. |
| 5 | [`screenshots/05_alert_fired.png`](screenshots/05_alert_fired.png) | The analyst-facing SNS email alert was delivered. |
| 6 | [`screenshots/06_response_executed.png`](screenshots/06_response_executed.png) | The Security Hub workflow state reached `NOTIFIED`. |

## Terraform baseline
Terraform handled the AWS infrastructure only.

Included baseline artifacts:
- [`terraform/main.tf`](terraform/main.tf)
- [`terraform/variables.tf`](terraform/variables.tf)
- [`terraform/outputs.tf`](terraform/outputs.tf)
- [`terraform/terraform.tfvars.example`](terraform/terraform.tfvars.example)
- [`terraform/README.md`](terraform/README.md)

The Terraform layer creates:
- GuardDuty detector
- Security Hub enablement
- findings S3 bucket with lifecycle rule
- KMS key for GuardDuty export
- GuardDuty publishing destination
- SNS topic and subscription
- EventBridge alert rule and target
- EventBridge response rule and target
- Lambda function and IAM permissions

## S3 retention and Athena triage
![S3 lifecycle rule](screenshots/s3_lifecycle_rule.png)

The S3 bucket retains findings for later queries.

- Objects transition to Standard-IA after 30 days.
- Objects expire after 90 days.
- Athena queries are saved under [`queries/`](queries/).

Key artifacts:
- [`screenshots/02_exported_to_s3.png`](screenshots/02_exported_to_s3.png)
- [`screenshots/03_athena_query_result.png`](screenshots/03_athena_query_result.png)
- [`queries/00_create_guardduty_table.sql`](queries/00_create_guardduty_table.sql)
- [`queries/01_severity_by_day.sql`](queries/01_severity_by_day.sql)
- [`queries/02_top_finding_types.sql`](queries/02_top_finding_types.sql)
- [`queries/03_affected_resources.sql`](queries/03_affected_resources.sql)
- [`queries/04_findings_by_account.sql`](queries/04_findings_by_account.sql)

## Alert path proof
![SNS alert email](screenshots/05_alert_fired.png)

The alert workflow is intentionally simple and explicit:

- **Source:** GuardDuty native EventBridge event
- **Filter:** high-severity finding
- **Route:** EventBridge to SNS
- **Outcome:** analyst-facing email

Artifacts:
- [`automation/alerting/eventbridge_guardduty_high_severity_to_sns.json`](automation/alerting/eventbridge_guardduty_high_severity_to_sns.json)
- [`automation/alerting/README.md`](automation/alerting/README.md)
- [`screenshots/04_eventbridge_rule_matched.png`](screenshots/04_eventbridge_rule_matched.png)
- [`screenshots/05_alert_fired.png`](screenshots/05_alert_fired.png)

## Response path proof
![Security Hub workflow state set to NOTIFIED](screenshots/06_response_executed.png)

The response workflow updates the finding for triage:

- **Source:** Security Hub imported GuardDuty findings in ASFF
- **Filter:** GuardDuty findings with `Workflow.Status = NEW` and `RecordState = ACTIVE`
- **Route:** EventBridge to Lambda
- **Action:** `BatchUpdateFindings` sets workflow status to `NOTIFIED` and adds a note

Artifacts:
- [`automation/response/eventbridge_securityhub_guardduty_new_high_to_lambda.json`](automation/response/eventbridge_securityhub_guardduty_new_high_to_lambda.json)
- [`automation/response/lambda_handler.py`](automation/response/lambda_handler.py)
- [`automation/response/README.md`](automation/response/README.md)
- [`screenshots/06_response_executed.png`](screenshots/06_response_executed.png)

## ASFF and investigation pivots
![Security Hub ASFF finding JSON](screenshots/securityhub_asff_finding_json.png)

Security Hub matters here because it normalizes GuardDuty findings into **AWS Security Finding Format (ASFF)**. That gives the response workflow a stable finding record to act on and gives the analyst a clean investigation layer.

Useful pivots in this package:
- [`screenshots/securityhub_asff_finding_json.png`](screenshots/securityhub_asff_finding_json.png)
- [`screenshots/cloudtrail_createSampleFindings.png`](screenshots/cloudtrail_createSampleFindings.png)
- [`workbooks/case-view.md`](workbooks/case-view.md)
- [`notes/investigation_timeline.md`](notes/investigation_timeline.md)

## MITRE mapping and IOC pack
- MITRE write-up: [`mitre/mitre_mapping.md`](mitre/mitre_mapping.md)
- IOC pack: [`ioc/guardduty_indicators.csv`](ioc/guardduty_indicators.csv)

The mapping stays intentionally narrow. The sample finding supports proxy-anonymization behavior. It does not prove persistence, data theft, or impact.

## Recommendations
- Add retry and backoff logic around `BatchUpdateFindings` to reduce the effect of Security Hub throttling during bursty sample generation.
- Add a dead-letter queue or queue-based buffering if the response path is expanded beyond a lab.
- Route analyst alerts into a ticketing or chat channel after the SNS email baseline is validated.
- Keep Athena queries scoped tightly by time or prefix to control cost and improve triage speed.
- In a future version, use a disposable EC2 test asset and a containment-only runbook if you want to demonstrate quarantine instead of workflow-state update.

## Reproduction summary
1. Deploy the baseline with Terraform.
2. Confirm the SNS subscription.
3. Enable Security Hub before the batch you want the response workflow to process.
4. Generate GuardDuty sample findings.
5. Confirm S3 export and run Athena triage queries.
6. Validate the alert path with EventBridge monitoring and the SNS email.
7. Validate the response path with Lambda logs and Security Hub `NOTIFIED` state.
8. Record timestamps and destroy the infrastructure.

## Artifact index
- `screenshots/` — ordered proof chain plus lifecycle, CloudTrail, ASFF, and architecture screenshots
- `automation/` — separate alerting and response workflow artifacts
- `queries/` — Athena triage SQL files
- `workbooks/` — AWS-native case-view walkthrough
- `mitre/` — ATT&CK mapping
- `ioc/` — sanitized indicators
- `notes/` — cost, cleanup, redaction, and investigation notes
- `terraform/` — IaC baseline
