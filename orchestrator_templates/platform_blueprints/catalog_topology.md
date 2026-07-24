# Enterprise Data Platform Catalog Topology & Storage Architecture

## 1. Unified Environment & Catalog Segmentation
The data platform enforces absolute logical separation of data environments across all processing engines (Azure Synapse, Microsoft Fabric, and Azure Databricks). This abstraction layers physical cloud storage paths (ADLS Gen2 / OneLake) into an ANSI-compliant three-tier catalog namespace:

```text
[environment_catalog]  ──>  [data_domain_schema]  ──>  [database_object]
```

### A. Operational Environments Matrix
- **`prod_catalog`**: Production storage layer. Write access is strictly denied to user accounts and restricted solely to automated deployment service principals. It holds verified datasets utilized for business operations and executive reporting dashboards.
- **`test_catalog`**: Staging and automated regression workspace. It mirrors production data structures using masked or synthetic data profiles to allow end-to-end pipeline validation before deployment.
- **`dev_catalog`**: Ephemeral development sandbox. Data engineers have full Read/Write permissions to prototype tables, test code logic, and iterate schemas. Data within this layer follows an automated 30-day purge lifecycle.

---

## 2. Medallion Layer Architecture & Functional Boundaries
Data domain schemas within each catalog are explicitly organized into a standardized Medallion progression model to enforce data quality and clean processing lineage.

```text
  [Raw Sources] 
        │
        ▼
┌───────────────┐
│ RAW / BRONZE  │ ──> Append-Only Immutable Ledger (Parquet / Delta)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ CONFORMED /   │ ──> Standardized snake_case, Cleansed, Enforced Schema,
│    SILVER     │     Atomic MERGE / Upsert Operations
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ ANALYTICS /   │ ──> Star Schema Dimensional Model (Fact/Dim Tables),
│     GOLD      │     Optimized Views & Analytical Functions
└───────────────┘
```

### A. Raw / Ingestion Layer (`brz_`)
- **Purpose:** Acts as the landing pad and permanent immutable history ledger of raw source files.
- **Storage Constraints:** Data is stored in optimized file types (Delta or Parquet) matching the exact schema structure of the source systems.
- **Processing Guardrails:** Direct transformations, formatting corrections, or business-logic filtering are strictly forbidden. Mutations are append-only.

### B. Conformed / Core Transformation Layer (`slv_`)
- **Purpose:** Serves as the enterprise "single source of truth" where disparate source domains are integrated and cleaned.
- **Data Quality Requirements:** All data types are explicitly declared, column headings are standardized to lowercase `snake_case`, and string nulls are completely eliminated.
- **Mutation Pattern Alignment:** In alignment with `programming_python.md`, changes to this layer must rely on atomic partition overwrites (`replaceWhere`) or row-level `MERGE` operations. Blind deletions or duplicate row entries are blocked.

### C. Analytical / Business Access Layer (`gld_`)
- **Purpose:** Holds business-ready aggregates and dimensional models optimized for BI platforms, corporate reporting, and machine learning features.
- **Structure Pattern Alignment:** Modeled as clean Kimball Star Schemas consisting of Fact (`fct_`) and Dimension (`dim_`) structures. 
- **Object Governance:** To secure baseline metrics, physical tables are abstracted using standardized presentation layers (views) and access-controlled via Table-Valued Functions (TVFs) defined in `schema_ddl.md`.

---

## 3. Cross-Layer Governance & Access Security
- **Catalog Isolation:** Cross-catalog queries (e.g., a development script querying production schemas directly) are blocked at the infrastructure firewall level.
- **Credential Protection:** In alignment with `schema_ddl.md`, all cross-layer operations reading from external unmanaged storage locations must authorize via independent, centrally audited encryption identities (`ext_scoped_credentials`).
- **Telemetry Hooks:** Every operational shift of data transitioning between layers (Bronze to Silver, or Silver to Gold) must hook directly into the decoupled schema payload contract defined in `alerting_system.md`.
