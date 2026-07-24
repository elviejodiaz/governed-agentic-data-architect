# Governed Agentic Data Architect 🤖💼

An enterprise-grade, policy-enforced AI Agent framework designed to autonomously generate compliant data engineering assets, validate architecture logic, and manage downstream repository delivery lifecycles using the Gemini API.

## 🚀 Architectural Vision

Traditional GenAI code assistants function as passive completion layers, frequently introducing security holes, naming violations, and unoptimized queries. This framework introduces a decoupled **Control Plane / Data Plane Architecture** that wraps the LLM inside a deterministic constraint engine.

```text
       [USER PROMPT] (e.g., "Create Silver Customers Upsert Pipeline")
             │
             ▼
 ┌────────────────────────────────────────────────────────┐
 │ CONTROL PLANE (governed-agentic-data-architect)        │
 │                                                        │
 │ 📂 config_engine/         ──> Instruction Mappings     │
 │ 📂 policy_guardrails/     ──> PySpark / SQL Standards  │
 │ 📂 platform_blueprints/   ──> Catalog & ADF Layouts    │
 │ 📂 solution_patterns/     ──> Alerting JSON Contracts  │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼ (Assembles Policy Payload)
                    ┌─────────────────┐
                    │ Gemini API Loop │ ──> Enforces low-temperature compliance
                    └────────┬────────┘
                             │
                             ▼ (Extracts Clean Source Files)
 ┌────────────────────────────────────────────────────────┐
 │ DATA PLANE (data-ops-generated-artifacts)              │
 │                                                        │
 │ 📂 database_deployment/   ──> Modular Tables & Views   │
 │ 📂 Wiki/                  ──> Auto-Generated Solutions │
 └────────────────────────────────────────────────────────┘
```

## 🛠️ Core Technological Core Capabilties

- **Decoupled Cross-Repository Isolation:** The agent segregates control assets from production features. Core laws live in one repository, while deployable features are dropped straight into a downstream repository.
- **Strict Idempotency Enforcement:** Blocks fragile pattern mutations (`DELETE` + `INSERT`). Automatically rewrites data loads to use native Delta Lake `Merge` operations and atomic partition overwrites (`replaceWhere`).
- **Event-Driven Alerting Injection:** Automatically forces the AI to embed structured HTTP JSON REST callbacks directly inside execution catch blocks, keeping data loading logic separate from destination alert endpoints (Teams, SMS, Email).
- **Automated Git Lifecycle Loops:** Programmatically orchestrates your version control. Checks out a clean feature branch, stages the generated files using relative indices, commits with tracing tags, and pushes to remote origins.

## 📁 Repository Structure

- `config_engine/`: Central hub mapping matrix files.
- `policy_guardrails/`: Strict naming conventions and language boundaries (Python, PySpark, SQL).
- `platform_blueprints/`: Platform environment definitions for Lakehouse catalogs and ADF layouts.
- `solution_patterns/`: Reusable alerting, database tree, and wiki documentation layout templates.
- `orchestrator_templates/`: System prompts used to structure inquiries to Gemini models.
- `run_agent.py`: The main controller engine managing text ingest, API bindings, and Git tasks.
