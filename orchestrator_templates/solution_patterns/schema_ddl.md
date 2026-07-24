# Enterprise Database-as-Code & Schema Deployment Layout Standards

## 1. Architectural Philosophy (Database-as-Code)
Every state change, structural mutation, or programmable object within relational and Lakehouse platforms (such as Azure Synapse, Microsoft Fabric, or Databricks Spark SQL) must be treated as an isolated, deployable artifact. 
- Consolidation of unrelated database objects into a single file is strictly prohibited.
- All definitions must be idempotent (`CREATE OR REPLACE` or check for existence via `IF NOT EXISTS`).

## 2. Directory Tree Layout Specification
When the agent generates or documents a database deployment, it must organize the file tree using this explicit object-hierarchy mapping matrix:

```text
📦 asset_database_deployment/
 ┣ 📁 security/                  # Security boundaries & credentials
 ┃ ┣ 📜 ext_scoped_credentials.sql
 ┃ ┗ 📜 database_roles.sql
 ┣ 📁 schemas/                   # Relational namespace boundaries
 ┃ ┗ 📜 sch_silver_sales.sql
 ┣ 📁 tables/                    # Physical and External Delta tables
 ┃ ┣ 📜 tbl_slv_orders.sql
 ┃ ┗ 📜 tbl_slv_customers.sql
 ┣ 📁 views/                     # Logical abstraction layers
 ┃ ┗ 📜 vw_gld_monthly_sales.sql
 ┣ 📁 functions/                 # Programmable computing blocks
 ┃ ┣ 📁 scalar_valued/           # Returns a single data point (SVF)
 ┃ ┃ ┗ 📜 fn_clean_string.sql
 ┃ ┗ 📁 table_valued/            # Returns an inline tabular dataset (TVF)
 ┃   ┗ 📜 fn_get_active_orders.sql
 ┗ 📁 stored_procedures/         # Orchestrated DML operations
   ┗ 📜 sp_optimize_delta_partitions.sql
```

## 3. Object-Specific Structural Mandates

### A. Security & Scoped Credentials (`security/`)
- External access tokens, Managed Identity bindings, or database-scoped credentials must use abstract configuration parameters. Hardcoded secret values are strictly forbidden.
- Scripts must explicitly define authorization roles (`CREATE ROLE` / `GRANT EXECUTE TO`).

### B. Programmable Functions (`functions/`)
- **Scalar-Valued Functions (SVF):** Must implement strict deterministic declarations where applicable (`DETERMINISTIC` or engine equivalent) to allow optimal compilation.
- **Table-Valued Functions (TVF):** Must use explicit column alias mappings inside the return block signature to prevent downstream dependency breaks if the underlying physical tables alter sequence order.

### C. Tables & Metadata Schema Constraints (`tables/`)
- Every physical table script must declare:
  1. Data type lengths explicitly (no reliance on default engine fallbacks).
  2. Nullability parameters (`NOT NULL` vs `NULL`).
  3. Table-level structural configurations at the footer block (e.g., `USING DELTA`, partition specifications, or file distribution paths).
