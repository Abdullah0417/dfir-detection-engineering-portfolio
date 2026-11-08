# OIDC setup record

## Purpose

This note records the GitHub OIDC trust path used for the Lab 06 test deployment proof without publishing the full set of local object IDs and resource IDs.

## GitHub side

- Org: `Abdullah0417`
- Repository name at the time of the recorded run: `dfir-labs`
- Current repository: `dfir-detection-engineering-portfolio`. Before rerunning deployment, verify that the Azure federated credential subject matches the current repository and `sentinel-test` environment. The historical screenshots do not verify the current trust configuration.
- Environment: `sentinel-test`
- Protection mode: required reviewer enabled, protected branch deployment gate in place

## Azure side

- App registration display name used for the OIDC trust: `dfir-lab06-gh-oidc-test-20260313`
- Federated credential name: `github-sentinel-test`
- Audience: `api://AzureADTokenExchange`
- Scope used for validation: Contributor at the Lab 06 test resource group scope

## What was verified

- The federated credential was created for the GitHub environment trust path.
- The Lab 06 test resource group had the required Contributor assignment for the OIDC service principal.
- The GitHub environment gate was configured before the smoke test and deploy runs.
- The smoke-test workflow approved successfully, logged in to Azure with OIDC, and confirmed access to the Lab 06 test workspace.
- The deploy workflow passed the gate again and completed the controlled test deployment path.

## Proof screenshots

- [Azure portal federated credential](../screenshots/14_azure_portal_federated_credential.png)
- [GitHub environment configuration](../screenshots/15_github_environment.png)
- [Environment approval gate](../screenshots/16_environment_approval_gate.png)
- [OIDC RBAC assignment](../screenshots/17_oidc_rbac_assignment.png)
- [OIDC smoke-test login success](../screenshots/18_oidc_smoke_test_login_success.png)
- [OIDC active account confirmed](../screenshots/19_oidc_active_account_confirmed.png)
- [OIDC smoke-test resource group confirmed](../screenshots/20_oidc_smoke_test_rg_confirmed.png)
- [Deploy approval gate](../screenshots/23_deploy_approval_gate.png)
- [Test workspace deploy success](../screenshots/25_test_workspace_deploy_success.png)

## Publish-safety note

The exact app IDs, object IDs, service principal IDs, subscription-scope resource IDs, and workflow run IDs were kept out of this public note on purpose. They were useful during execution, but they are not needed to explain or prove the trust path.
