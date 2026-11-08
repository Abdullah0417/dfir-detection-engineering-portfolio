## Objective
Validate end-to-end Windows telemetry ingestion (Heartbeat + Sysmon + Security auth) into Microsoft Sentinel using AMA + DCR, with no public RDP exposure.


## Environment
- Resource Group: rg-dfir-lab-scus
- Region: South Central US
- VM: win-ws1 (Windows Server 2022 Datacenter: Azure Edition - Gen2)
- SIEM: Microsoft Sentinel
- Log Analytics Workspace: law-dfir
- Collection: Azure Monitor Agent (AMA) + Data Collection Rule (DCR)
- Evidence root(local, not published casework): C:\Evidence\Cases\2026-01-29_WinWS1_TestIR
- Lab directory: `labs/01-telemetry-siem-validation/`

## What I configured
- Deployed `win-ws1` in a lab VNet and enforced network access controls (no open Internet RDP)
- Enabled Microsoft Sentinel on `law-dfir`
- Installed/verified Azure Monitor Agent on the VM
- Associated the VM to the DCR to ingest Security + Sysmon logs
- Validated ingestion end-to-end using KQL and captured proof screenshots

## Results (validated in Sentinel)
- Heartbeat ingestion: PASS (latest `TimeGenerated`: 2026-02-05T22:12:50Z)
- Sysmon ingestion: PASS (latest Sysmon event `TimeGenerated`: 2026-02-05T22:13:29Z)
- Security auth ingestion: PASS (latest 4624/4625 `TimeGenerated`: 2026-02-05T22:11:24Z)
- Inbound 3389 allowed only from Bastion subnet / Azure Bastion; no 3389 from Internet

## Evidence (screenshots)
- [Resource group overview](screenshots/01_rg_overview.png) — RG inventory proof
- [VM overview](screenshots/02_vm_overview.png) — VM configuration proof
- [DCR data sources](screenshots/03_dcr_data_sources.png) — DCR configured
- [DCR resources assignment](screenshots/03_dcr_resources.png) — VM associated to DCR
- [AMA extension](screenshots/04_vm_ama_extension.png) — AMA installed
- [KQL: Heartbeat](screenshots/05_kql_heartbeat.png) —  Heartbeat confirms agent connectivity + ingestion
- [KQL: Heartbeat chart](screenshots/05_kql_heartbeat_ot_chart.png) — Heartbeat trend over time 
- [KQL: Sysmon](screenshots/06_kql_sysmon.png) — Sysmon events present in Log Analytics (EventLog + EventID)
- [KQL: Sysmon chart](screenshots/06_kql_sysmon_ot_chart.png) — Sysmon event volume over time
- [KQL: Security auth 4624/4625](screenshots/07_kql_security_auth.png) — Auth telemetry present (successful/failed logons)
- [NSG inbound](screenshots/08_nsg_inbound.png) — Network access control proof

## Queries (KQL)
- [Heartbeat win-ws1](kql/01_heartbeat_win-ws1.kql)
- [Sysmon recent](kql/02_sysmon_recent.kql)
- [Security auth (4624/4625)](kql/03_security_auth_4624_4625.kql)
- [event log volume last 1hr](kql/04_event_log_volume_last_1h.kql)

## Check ingestion in an existing lab
1. Open Sentinel → Logs (law-dfir).
2. Run the KQL files in `/kql` in order.
3. Confirm rows return for Heartbeat, Sysmon, and Security events.
4. Compare output to screenshots in `/screenshots`.
