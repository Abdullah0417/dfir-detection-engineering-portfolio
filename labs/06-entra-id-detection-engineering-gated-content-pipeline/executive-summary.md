# Lab summary — Entra ID detections

I used controlled Entra ID activity to build three Sentinel detections: failed sign-in bursts, directory role changes, and service principal update candidates. The lab includes the KQL, rule exports, an incident-tagging rule, a workbook, and screenshots of the recorded runs.

The GitHub Actions workflow uses OIDC to authenticate to Azure, validates and packages content, checks an ARM what-if result, and deploys a workbook to a separate test workspace after environment approval. The Bicep wrapper deploys only the workbook. Analytics and automation exports require separate import and testing.

The service principal query also matches general updates; its results require review before confirming a credential addition. The queries need tuning for shared IP addresses, normal administrative changes, and the events available in the target tenant. Static validation does not execute KQL or establish detection accuracy. See the [lab README](README.md) for evidence and reproduction notes.
