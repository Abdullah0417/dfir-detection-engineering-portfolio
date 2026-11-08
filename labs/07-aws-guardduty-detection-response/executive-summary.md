# Lab summary — AWS GuardDuty findings

I used Terraform to configure GuardDuty, Security Hub, S3 retention, EventBridge, SNS, and a response Lambda in a single AWS Region. Athena queries inspect the exported findings. GuardDuty sample findings supplied the test data.

The alert path sends SNS email. The response path calls Security Hub `BatchUpdateFindings` to set workflow status to `NOTIFIED` and add a note. This is a triage status update; it does not isolate resources, revoke access, or confirm remediation.

Security Hub was enabled after the first batch of sample findings. The lab notes report successful Lambda updates for a second batch. One finding was also updated manually by CLI. The console screenshot of `NOTIFIED` shows the final state, but cannot independently attribute that change to Lambda.

Start with the [Athena results](screenshots/03_athena_query_result.png), [SNS email](screenshots/05_alert_fired.png), and [response state](screenshots/06_response_executed.png). The [lab README](README.md) links the code and investigation notes. These are recorded lab results, not a current deployment check.
