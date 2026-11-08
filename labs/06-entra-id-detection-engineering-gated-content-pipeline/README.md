# Microsoft Entra ID Detection Engineering + Gated Sentinel Content-as-Code Pipeline

[![Lab 06 workbook hero](screenshots/13_workbook_identity_dashboard.png)](screenshots/13_workbook_identity_dashboard.png)

## What I tested

- I validated Microsoft Entra ID telemetry in Microsoft Sentinel before I wrote detections.
- I built and tested identity-focused KQL against real Entra activity, including failed sign-in bursts, directory role changes, and service principal credential changes.
- I promoted the strongest hunts into scheduled analytics with MITRE mapping, entity mapping, incident creation, and exported rule artifacts.
- I added a lightweight response layer with an automation rule and a focused workbook so the lab shows an analyst workflow instead of isolated query output.
- I exported the content as code and then proved the gated path into a separate test workspace with GitHub OIDC, validation checks, packaging, ARM `what-if`, approval, and a controlled test deployment.

The deployment workflow creates a workbook in the test workspace. Analytics and automation rules are included as separate exports.

## Scenario and scope

This lab uses controlled identity activity in Microsoft Sentinel.

The goal was to show that I can take Entra telemetry from connector validation through hunt development, scheduled analytics, incident handling, workbook presentation, export the content as code, and then move that content through a gated test deployment path.

The lab centers on three primary scenarios:

1. A failed sign-in burst from one source IP across multiple users  
2. A directory role assignment change involving the Security Reader role  
3. A service principal credential addition on a dedicated lab service principal  

I used one authoring workspace for building and validating the content and a separate test workspace for the OIDC and gated deployment proof path.

## Data sources used

Primary Entra tables used in this lab:

- `AuditLogs`
- `SigninLogs`
- `AADServicePrincipalSignInLogs` for connector and table validation where applicable

The detections in this lab rely mainly on:

- `SigninLogs` for failed sign-in burst logic and the related success-after-failure hunt
- `AuditLogs` for directory role assignment changes
- `AuditLogs` for service principal credential changes

## Workflow

I kept the workflow simple and deliberate:

1. **Validate telemetry first**  
   Confirm the Entra connector was enabled and prove the required tables were populated before writing detection logic.

2. **Build the hunts around real activity**  
   Run each identity scenario in a controlled way, then verify the exact fields and `OperationName` values that showed up in the tenant.

3. **Promote stable logic into analytics**  
   Convert the strongest hunts into scheduled analytics with thresholds, MITRE mapping, entity mapping, and incident creation enabled.

4. **Add investigation and response context**  
   Create one automation rule and one workbook so the lab shows how an analyst would review and triage the results.

5. **Export the content as code**  
   Save the analytics, automation, and workbook artifacts in repo-safe JSON so the work is reviewable and reusable.

6. **Prove the gated test deployment path**  
   Use GitHub OIDC, validation checks, packaging, ARM `what-if`, approval, and a controlled deployment into the separate test workspace.

## Pipeline and gated deployment

The deployment evidence covers:

- federated credential setup for the GitHub environment
- protected environment approval
- successful OIDC login into Azure
- content validation and package creation
- ARM `what-if` review before deployment
- deployment of the lightweight workbook wrapper into the Lab 06 test workspace

The current what-if check permits `Create`, `Modify`, and `NoChange`. It stops on deletion, incomplete or unknown change types, failed operations, and malformed results.

The Bicep deployment creates the workbook only. The analytics and automation exports need separate import and validation.

**Artifacts**
- [pipeline/manifests/content-manifest.json](pipeline/manifests/content-manifest.json)
- [pipeline/deploy/main.bicep](pipeline/deploy/main.bicep)
- [pipeline/deploy/workbook.serialized.json](pipeline/deploy/workbook.serialized.json)
- [pipeline/parameters/test.parameters.json](pipeline/parameters/test.parameters.json)
- [notes/oidc-setup.md](notes/oidc-setup.md)

**Proof**
- [Azure portal federated credential](screenshots/14_azure_portal_federated_credential.png)
- [GitHub environment configuration](screenshots/15_github_environment.png)
- [Environment approval gate](screenshots/16_environment_approval_gate.png)
- [OIDC RBAC assignment](screenshots/17_oidc_rbac_assignment.png)
- [OIDC smoke-test login success](screenshots/18_oidc_smoke_test_login_success.png)
- [OIDC active account confirmed](screenshots/19_oidc_active_account_confirmed.png)
- [OIDC smoke-test resource group confirmed](screenshots/20_oidc_smoke_test_rg_confirmed.png)
- [PR validation checks](screenshots/21_pr_validation_checks.png)
- [Package dist artifact](screenshots/22_package_dist_artifact.png)
- [Deploy approval gate](screenshots/23_deploy_approval_gate.png)
- [ARM what-if output](screenshots/24_arm_whatif_output.png)
- [Test workspace deploy success](screenshots/25_test_workspace_deploy_success.png)
- [Test workspace content inventory](screenshots/26_test_workspace_content_inventory.png)

## Key findings

### Failed sign-in burst activity was easy to isolate in `SigninLogs`

The hunt surfaced one IP failing against multiple lab users inside a short window. That gave me a clean identity detection candidate with straightforward tuning logic.

Related proof:
- [Failed sign-in burst hunt](screenshots/04_failed_signin_burst_hunt.png)
- [Successful sign-in after failure burst hunt](screenshots/05_success_after_failure_burst_hunt.png)

### A later success from the same IP added useful investigation context

The success-after-failure query is a hunt for investigation. The failed-burst query is the scheduled analytic.

Related proof:
- [Successful sign-in after failure burst hunt](screenshots/05_success_after_failure_burst_hunt.png)

### Directory role changes produced a high-value audit signal

The role-assignment scenario generated clear `AuditLogs` events tied to privilege changes. That made it a strong identity detection with obvious control-plane relevance.

Related proof:
- [Role assignment hunt](screenshots/06_role_assignment_hunt.png)
- [Directory role assignment analytic](screenshots/09_rule_role_assignment_change.png)
- [Identity incident triggered](screenshots/11_identity_incident_triggered.png)

### Service principal update candidates

The service principal scenario produced audit events that I used to investigate credential changes.

Related proof:
- [Service principal credential addition hunt](screenshots/07_sp_credential_addition_hunt.png)
- [Service principal credential addition analytic](screenshots/10_rule_sp_credential_addition.png)

## Detections

### Failed sign-in burst by IP

**Purpose**  
Detect repeated failed Microsoft Entra interactive sign-ins from a single IP across multiple users within a short time window.

**Why it matters**  
A burst across multiple users can indicate password spraying. Shared IP addresses and normal sign-in failures also need investigation.

**Artifacts**
- [kql/analytics/failed_signin_burst_by_ip.kql](kql/analytics/failed_signin_burst_by_ip.kql)
- [detections/docs/01_failed_signin_burst_by_ip.md](detections/docs/01_failed_signin_burst_by_ip.md)
- [detections/exports/analytics/rule_failed_signin_burst.json](detections/exports/analytics/rule_failed_signin_burst.json)

**Proof**
- [Failed sign-in burst analytic](screenshots/08_rule_failed_signin_burst.png)

### Directory role assignment change

**Purpose**  
Detect Microsoft Entra directory role assignment or role membership changes that may increase privilege or support persistence.

**Why it matters**  
It is a clean `AuditLogs` signal with obvious security impact and very little ambiguity about why it matters.

**Artifacts**
- [kql/analytics/directory_role_assignment_change.kql](kql/analytics/directory_role_assignment_change.kql)
- [detections/docs/02_directory_role_assignment_change.md](detections/docs/02_directory_role_assignment_change.md)
- [detections/exports/analytics/rule_role_assignment_change.json](detections/exports/analytics/rule_role_assignment_change.json)

**Proof**
- [Directory role assignment analytic](screenshots/09_rule_role_assignment_change.png)

### Service principal credential-change candidates

**Purpose**  
Detect the addition of a new password credential to a Microsoft Entra service principal.

**Why it matters**  
It adds cloud identity depth and shows awareness of persistence through app and service principal changes.

**Artifacts**
- [kql/analytics/service_principal_credential_addition.kql](kql/analytics/service_principal_credential_addition.kql)
- [detections/docs/03_service_principal_credential_addition.md](detections/docs/03_service_principal_credential_addition.md)
- [detections/exports/analytics/rule_sp_credential_addition.json](detections/exports/analytics/rule_sp_credential_addition.json)

**Proof**
- [Service principal credential addition analytic](screenshots/10_rule_sp_credential_addition.png)

## Incident automation

I kept the response layer intentionally light.

The automation rule triggers when a Lab 06 incident is created and applies a standard label so identity incidents are easier to triage consistently.

**Artifacts**
- [automation/exports/identity-triage-automation.export.json](automation/exports/identity-triage-automation.export.json)

**Proof**
- [Identity triage automation rule](screenshots/12_automation_rule_identity_triage.png)

## Workbook

The workbook is intentionally compact. The point was to give an analyst one place to review the most relevant identity signals, not to build a giant dashboard for its own sake.

It includes:

- Entra ingestion status
- failed sign-in candidates by IP
- directory role change activity
- service principal credential events

**Artifacts**
- [kql/workbook/01_ingestion_status.kql](kql/workbook/01_ingestion_status.kql)
- [kql/workbook/02_failed_signin_candidates.kql](kql/workbook/02_failed_signin_candidates.kql)
- [kql/workbook/03_role_change_timeline.kql](kql/workbook/03_role_change_timeline.kql)
- [kql/workbook/04_sp_credential_events.kql](kql/workbook/04_sp_credential_events.kql)
- [workbooks/exports/identity_dashboard.json](workbooks/exports/identity_dashboard.json)

**Proof**
- [Workbook identity dashboard](screenshots/13_workbook_identity_dashboard.png)

## MITRE mapping

The mappings describe the simulated behaviors and detection scope.

Current mappings include:

- **T1110** — brute-force or password-spraying style behavior
- **T1098** — account manipulation through role membership changes
- **T1098.001** — additional cloud credentials through service principal credential changes

**Artifact**
- [mitre/mitre_mapping.md](mitre/mitre_mapping.md)

## IOC and observable handling

This lab leans more on identity observables than traditional host-based IOCs.

Tracked observables include:
- the source IP used during failed sign-in testing
- the lab user identities involved in the burst scenario
- the role-target account used in the role assignment scenario
- role-change correlation identifiers
- service principal credential-change correlation identifiers
- the service principal display name used in the test scenario

**Artifact**
- [ioc/identity_observables.csv](ioc/identity_observables.csv)

## Notes and constraints

The service principal query includes broad `Update service principal` events. It can return unrelated or failed updates and is not restricted to the dedicated lab service principal. Review the result and modified properties before classifying a credential addition.

A few boundaries matter here:

- `AuditLogs` were the hard requirement. If `SigninLogs` had not been available, the lab would have shifted to an audit-heavy fallback instead of pretending sign-in visibility existed.
- The success-after-failure logic was useful hunt material, but I kept the primary scheduled detections focused on the cleaner signals.
- The automation rule tags incidents and sets severity.
- The workbook displays ingestion, sign-in, role-change, and credential-event views.
- OIDC deployment targets a separate test workspace and creates only the workbook.

## What I would improve next

If I extend this lab, the next steps are:

1. Add stricter tuning and exclusion handling for shared NAT or proxy noise in the failed sign-in rule  
2. Add a second validation pass for policy changes or authentication-method changes in `AuditLogs`  
3. Expand the deploy wrapper beyond the workbook-focused proof path used in this version  
4. Add a short tuning note pack for expected false-positive themes and normal admin-change noise  

## Reproduction notes

At a high level, this lab can be reproduced by:

1. enabling the Microsoft Entra connector in Sentinel  
2. validating `AuditLogs` and `SigninLogs` ingestion  
3. executing the three controlled identity scenarios  
4. building the raw hunts first  
5. promoting stable hunt logic into scheduled analytics  
6. creating one automation rule and one workbook  
7. exporting the resulting Sentinel content as repo-safe artifacts  
8. proving the OIDC, validation, package, `what-if`, approval, and test-deploy path  

Detailed execution notes live in:
- [notes/licensing-and-fallback.md](notes/licensing-and-fallback.md)
- [notes/scenario-execution.md](notes/scenario-execution.md)
- [notes/redactions.md](notes/redactions.md)
- [notes/oidc-setup.md](notes/oidc-setup.md)

## Artifact index

### Screenshots
- [screenshots/01_entra_connector_enabled.png](screenshots/01_entra_connector_enabled.png)
- [screenshots/02_auditlogs_validation.png](screenshots/02_auditlogs_validation.png)
- [screenshots/03_signinlogs_validation.png](screenshots/03_signinlogs_validation.png)
- [screenshots/04_failed_signin_burst_hunt.png](screenshots/04_failed_signin_burst_hunt.png)
- [screenshots/05_success_after_failure_burst_hunt.png](screenshots/05_success_after_failure_burst_hunt.png)
- [screenshots/06_role_assignment_hunt.png](screenshots/06_role_assignment_hunt.png)
- [screenshots/07_sp_credential_addition_hunt.png](screenshots/07_sp_credential_addition_hunt.png)
- [screenshots/08_rule_failed_signin_burst.png](screenshots/08_rule_failed_signin_burst.png)
- [screenshots/09_rule_role_assignment_change.png](screenshots/09_rule_role_assignment_change.png)
- [screenshots/10_rule_sp_credential_addition.png](screenshots/10_rule_sp_credential_addition.png)
- [screenshots/11_identity_incident_triggered.png](screenshots/11_identity_incident_triggered.png)
- [screenshots/12_automation_rule_identity_triage.png](screenshots/12_automation_rule_identity_triage.png)
- [screenshots/13_workbook_identity_dashboard.png](screenshots/13_workbook_identity_dashboard.png)
- [screenshots/14_azure_portal_federated_credential.png](screenshots/14_azure_portal_federated_credential.png)
- [screenshots/15_github_environment.png](screenshots/15_github_environment.png)
- [screenshots/16_environment_approval_gate.png](screenshots/16_environment_approval_gate.png)
- [screenshots/17_oidc_rbac_assignment.png](screenshots/17_oidc_rbac_assignment.png)
- [screenshots/18_oidc_smoke_test_login_success.png](screenshots/18_oidc_smoke_test_login_success.png)
- [screenshots/19_oidc_active_account_confirmed.png](screenshots/19_oidc_active_account_confirmed.png)
- [screenshots/20_oidc_smoke_test_rg_confirmed.png](screenshots/20_oidc_smoke_test_rg_confirmed.png)
- [screenshots/21_pr_validation_checks.png](screenshots/21_pr_validation_checks.png)
- [screenshots/22_package_dist_artifact.png](screenshots/22_package_dist_artifact.png)
- [screenshots/23_deploy_approval_gate.png](screenshots/23_deploy_approval_gate.png)
- [screenshots/24_arm_whatif_output.png](screenshots/24_arm_whatif_output.png)
- [screenshots/25_test_workspace_deploy_success.png](screenshots/25_test_workspace_deploy_success.png)
- [screenshots/26_test_workspace_content_inventory.png](screenshots/26_test_workspace_content_inventory.png)

### KQL
- [kql/validation/](kql/validation/)
- [kql/hunts/](kql/hunts/)
- [kql/analytics/](kql/analytics/)
- [kql/workbook/](kql/workbook/)

### Detection docs and exports
- [detections/docs/](detections/docs/)
- [detections/exports/analytics/](detections/exports/analytics/)

### Automation and workbook exports
- [automation/exports/](automation/exports/)
- [workbooks/exports/](workbooks/exports/)

### Pipeline files
- [pipeline/manifests/content-manifest.json](pipeline/manifests/content-manifest.json)
- [pipeline/deploy/main.bicep](pipeline/deploy/main.bicep)
- [pipeline/deploy/workbook.serialized.json](pipeline/deploy/workbook.serialized.json)
- [pipeline/parameters/test.parameters.json](pipeline/parameters/test.parameters.json)

### Notes
- [notes/licensing-and-fallback.md](notes/licensing-and-fallback.md)
- [notes/scenario-execution.md](notes/scenario-execution.md)
- [notes/redactions.md](notes/redactions.md)
- [notes/oidc-setup.md](notes/oidc-setup.md)

### MITRE and IOC support files
- [mitre/mitre_mapping.md](mitre/mitre_mapping.md)
- [ioc/identity_observables.csv](ioc/identity_observables.csv)
