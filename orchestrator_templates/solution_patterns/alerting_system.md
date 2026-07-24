# Enterprise Event-Driven Alerting & Incident Notification Architecture

## 1. Architectural Philosophy (Notification Abstraction)
Data engineering pipelines (PySpark notebooks, SQL procedures, or Data Factory orchestrators) must remain completely agnostic of the final notification delivery systems. 
- Direct hardcoding of destination protocols (e.g., SMTP servers, Teams webhook URLs, or SMS API keys) inside data processing layers is strictly prohibited.
- Pipelines must asynchronously emit a standardized, high-density telemetry payload over HTTPS REST to an Event Routing Layer (e.g., Azure Logic Apps, Azure Functions, or AWS Lambda).
- The Event Routing Layer evaluates the data payload, determines severity, and handles multi-channel alerting workflows (Teams, Email, SMS, WhatsApp).

## 2. Universal Telemetry Payload Specification (The Rest Contract)
Every automated data asset must target the centralized event router with a JSON payload structured exactly as follows:

```json
{
  "system_context": {
    "orchestration_engine": "Databricks | Fabric | ADF",
    "environment": "DEV | TEST | PROD",
    "pipeline_id": "string_uuid",
    "asset_name": "nb_transform_slv_orders"
  },
  "event_telemetry": {
    "timestamp": "YYYY-MM-DDTHH:mm:ssZ",
    "event_type": "PIPELINE_START | PIPELINE_SUCCESS | PIPELINE_WARNING | CRITICAL_FAULT",
    "records_affected": 0,
    "execution_duration_sec": 0.0
  },
  "incident_details": {
    "error_code": "string_or_null",
    "error_summary": "string_or_null",
    "stack_trace": "string_or_null"
  }
}
```

## 3. Event Router Workflow & Multi-Channel Delivery Logic
Once the Centralized Event Router (such as an **Azure Logic App**) intercepts the REST payload, it processes the request through a conditional execution matrix to notify stakeholders:

```text
[Data Asset Payload] ──> [Central REST Endpoint] ──> [Event Router (Logic App)]
                                                            │
            ┌───────────────────┼───────────────────────────┴─────────────────────┐
            ▼                   ▼                           ▼                     ▼
     [CRITICAL_FAULT]    [PIPELINE_WARNING]         [PIPELINE_SUCCESS]     [SLA_BREACH]
            │                   │                           │                     │
   (On-Call Escalation)  (Team Slack/Teams)          (Metadata Warehouse)   (Management SMS)
            │                   │                           │                     │
  ┌─────────┴─────────┐         ▼                           ▼                     ▼
  ▼                   ▼     Post message to            Log duration &      Fire Twilio SMS
PagerDuty          Office365   "Data-Ops-Alerts"       row-counts into      or WhatsApp alert
Trigger            Email-Blast  Teams Channel          Lineage Catalog      to Data Director
```

### A. Critical Fault Routing (Immediate Action Required)
- **Trigger Condition:** `event_type == "CRITICAL_FAULT"` in a `PROD` environment.
- **Workflow Action:** The router triggers immediate on-call escalation via PagerDuty/Opsgenie APIs, fires an urgent high-priority Email via Office365, and executes a high-impact Microsoft Teams adaptive card broadcast.

### B. Pipeline Warning Routing (Non-Breaking Issues)
- **Trigger Condition:** `event_type == "PIPELINE_WARNING"` (e.g., partial schema mismatch, unexpected null percentages handled by the pipeline).
- **Workflow Action:** The router drops an operational digest message into the engineering team's Microsoft Teams or Slack `#data-ops-alerts` channel. No on-call pages are triggered.

### C. SLA and External Vendor Notifications (SMS / WhatsApp)
- **Trigger Condition:** Specific business-critical pipelines stall or fail to report execution data within their allocated timeline.
- **Workflow Action:** The router spins up programmatic webhooks targeting communication aggregators (e.g., Twilio or Infobip) to push automated SMS or WhatsApp mobile notifications straight to production support managers.

## 4. PySpark Reference Implementation
All PySpark notebooks must wrap their main orchestration code inside a try-except layer that enforces this decoupled contract:

```python
import requests
from datetime import datetime

def dispatch_event(event_type: str, asset: str, records: int = 0, err: Exception = None):
    url = "https://enterprise-gateway.com"
    
    payload = {
        "system_context": {
            "orchestration_engine": "Databricks_Spark",
            "environment": "PROD",
            "pipeline_id": "db-run-12345",
            "asset_name": asset
        },
        "event_telemetry": {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event_type": event_type,
            "records_affected": records,
            "execution_duration_sec": 42.5
        },
        "incident_details": {
            "error_code": type(err).__name__ if err else None,
            "error_summary": str(err) if err else None,
            "stack_trace": "Detailed trace would be extracted here" if err else None
        }
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as network_fault:
        print(f"[FATAL] Telemetry layer unreachable: {str(network_fault)}")

# Main Notebook Execution Loop
try:
    # Business logic transformations go here
    records_processed = 50000
    dispatch_event("PIPELINE_SUCCESS", "nb_transform_slv_orders", records=records_processed)
except Exception as notebook_error:
    dispatch_event("CRITICAL_FAULT", "nb_transform_slv_orders", err=notebook_error)
    raise notebook_error
```
