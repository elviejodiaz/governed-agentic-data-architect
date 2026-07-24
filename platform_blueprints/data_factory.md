# Azure Data Factory & Microsoft Fabric Pipeline Architecture

## 1. Unified Control Flow Blueprint
Every orchestration pipeline blueprint (`pl_`) must follow a strict linear design pattern split into three clear execution zones:
1. **System Initialization:** Pre-execution verification utilizing a Lookup or Web activity to ensure source file systems, external landing zones, or database APIs are responsive before computing resources are spun up.
2. **Core Payload Processing:** Execution of copy tasks or execution of transformation notebooks (`nb_`). Hardcoded compute cluster IDs are forbidden; clusters must be selected via dynamic enterprise pool parameters.
3. **Pipeline Lifecycle Finalization:** Conditional branches triggering independent metadata logging or routing structural data to the centralized event router.

## 2. Parameterization and Security Mandates
- **Dynamic Content Injection:** Pipelines must never hardcode source paths, connection details, container endpoints, environment labels, or target execution timestamps. These must be abstracted using runtime expressions (e.g., `@pipeline().parameters.TargetExecutionDate`).
- **Secret Extraction Architecture:** Injecting text connection strings or passwords into pipeline JSONs is strictly prohibited. Pipelines must dynamically pull authentication parameters from a managed password Vault via secure parameter references.
- **Secure Inputs & Outputs:** Both "Secure Input" and "Secure Output" checkboxes must be activated on every activity dealing with access tokens, parameters, or external rest calls to keep passwords out of the operational execution logging dashboards.
