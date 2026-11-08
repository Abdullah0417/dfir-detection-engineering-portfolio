# DFIR and Detection Engineering Labs

Seven security labs covering Windows telemetry, incident timelines, endpoint artifacts, Microsoft Entra ID detections, and AWS GuardDuty findings. Each lab includes queries or code, screenshots from the lab, and notes on the results and limitations.

## Start here

- [04 — Endpoint forensics](labs/04-endpoint-forensics-casework/): follow a benign scheduled-task scenario through MFT and event-log analysis into Sentinel detections.
- [06 — Entra ID detections](labs/06-entra-id-detection-engineering-gated-content-pipeline/): review three identity detections and a GitHub Actions workflow that deploys a workbook to a test workspace.
- [07 — GuardDuty findings](labs/07-aws-guardduty-detection-response/): trace sample findings through S3, Athena, email notification, and a Security Hub workflow-status update.

## Labs

| Lab | Work covered | Main limitation |
| --- | --- | --- |
| [01 — Telemetry and SIEM validation](labs/01-telemetry-siem-validation/) | Check AMA/DCR collection of Heartbeat, Sysmon, and Windows Security events | Results describe the configured lab hosts and capture window |
| [02 — Incident reconstruction](labs/02-incident-reconstruction/) | Build a timeline across two Windows hosts and detect encoded PowerShell | Benign test activity; encoded commands alone do not establish malicious intent |
| [03 — Telemetry coverage](labs/03-controls-to-telemetry-audit/) | Generate test events and compare observed coverage across hosts | Missing events can mean missing test activity; they do not automatically prove a collection failure |
| [04 — Endpoint forensics](labs/04-endpoint-forensics-casework/) | Correlate MFT and EVTX artifacts from a scheduled-task scenario | Controlled simulation; raw evidence remains local |
| [05 — Process-memory investigation](labs/05-memory-forensics-cloud-secops-loop/) | Recover canary strings from a process dump and correlate Sentinel events | Full-RAM Volatility analysis did not succeed; command-line decoding and memory strings are separate evidence sources |
| [06 — Entra ID detections and workbook deployment](labs/06-entra-id-detection-engineering-gated-content-pipeline/) | Build identity detections, incident tagging, a workbook, and an OIDC deployment workflow | The deployment wrapper creates the workbook; analytics and automation are separate exports |
| [07 — GuardDuty detection and triage](labs/07-aws-guardduty-detection-response/) | Query sample findings, send SNS alerts, and update Security Hub findings with Lambda | Sample findings; the response updates workflow status and does not contain an attack |

## Tools used

- Microsoft Sentinel, Log Analytics, Microsoft Entra ID, KQL, AMA/DCR
- Sysmon, Windows event logs, KAPE, MFTECmd, EvtxECmd, Timeline Explorer
- Process dumps and strings extraction; attempted Volatility 3 analysis documented in Lab 05
- GuardDuty, Security Hub, EventBridge, SNS, Lambda, S3, Athena, and KMS
- GitHub Actions, Azure Bicep, Terraform, and GitHub OIDC

## Using the material

Start with a lab README and its evidence links. Queries and templates use lab-specific hosts, tables, resource names, and thresholds; review those values before trying them in your own disposable environment. Cloud deployments can incur costs. Follow each lab's cleanup notes.

Screenshots record earlier lab runs. Offline checks validate selected code and content; they do not replay those investigations or verify a current cloud deployment. Detection rules need tuning for normal administrative activity.

Raw event logs, memory dumps, credentials, and Terraform state belong outside this repository. See the lab notes for collection methods and redactions.

## Offline checks

GitHub Actions runs Python unit tests and the Lab 06 content validators, plus mocked Pester tests for the Lab 03 harness. From the repository root:

```text
python -m pip install pyyaml
python -m unittest discover -s tests -v
```

With Pester 5.7.1 loaded, run `Invoke-Pester ./tests/Lab03Harness.Tests.ps1`. These tests mock local account/task commands and AWS calls. KQL and Athena queries still require testing against the relevant lab data. Local Windows PowerShell 5.1 testing was blocked by a Pester module-loading policy; the harness tests have been run with PowerShell 7.

## Possible next labs

AWS IAM/S3 misconfiguration investigation and EKS security are planned topics. No completed results are claimed for them here.
