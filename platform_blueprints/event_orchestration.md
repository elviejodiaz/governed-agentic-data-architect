# Inbound Pipeline-to-Event-Router Rest API Integration

## 1. Orchestration Webhook Protocol
In alignment with `solution_patterns/alerting_system.md`, data pipelines must actively report operational states (successes, warnings, and faults) by triggering an asynchronous HTTPS POST REST call to the decoupled central Event Router endpoint (Azure Logic App).

## 2. Data Factory Web Activity Implementation Blueprint
When the agent generates or modifies an Azure Data Factory or Microsoft Fabric pipeline JSON schema, it must append a final **Web Activity** configured with these explicit technical boundaries:
- **Activity Method:** `POST`
- **Activity Target URL:** `@pipeline().parameters.CentralEventRouterUrl` (Dynamically injected via parameters).
- **Secure Input / Secure Output:** Enabled (`true`).

## 3. Mandatory Dynamic JSON Payload Mapping
The body payload constructed inside the Web Activity expression box must evaluate and map the pipeline's runtime system variables to match the global schema contract:

```json
{
  "system_context": {
    "orchestration_engine": "Azure_Data_Factory",
    "environment": "@pipeline().DataFactory",
    "pipeline_id": "@pipeline().RunId",
    "asset_name": "@pipeline().Pipeline"
  },
  "event_telemetry": {
    "timestamp": "@utcnow('yyyy-MM-ddTHH:mm:ssZ')",
    "event_type": "pipeline_conditional_evaluation_token", 
    "records_affected": -1,
    "execution_duration_sec": 0.0
  },
  "incident_details": {
    "error_code": "@activity('Core_Payload_Activity').Error?.errorCode",
    "error_summary": "@activity('Core_Payload_Activity').Error?.message",
    "stack_trace": "@string(activity('Core_Payload_Activity').Error)"
  }
}
```

## 4. Conditional Activity Chaining Rules
- **OnSuccess Routing:** If the main payload task succeeds, a web activity must fire with `event_type` explicitly hardcoded to `"PIPELINE_SUCCESS"`.
- **OnFailure Routing:** If the main payload task fails, an independent web activity linked via a dependency failure line must execute, catching the upstream error log parameters and setting `event_type` to `"CRITICAL_FAULT"`.
