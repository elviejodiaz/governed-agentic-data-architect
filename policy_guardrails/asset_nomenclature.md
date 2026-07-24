# Enterprise Data Platform Naming & Nomenclature Standards

## 1. Medallion Storage Layer Namespaces
All catalogs, schemas, and relational tables must follow the lower_snake_case pattern utilizing specific layer prefixes:
- **Bronze (Ingestion):** `brz_[source_system]_[entity_name]` (e.g., `brz_sap_billing_items`)
- **Silver (Conformed):** `slv_[business_domain]_[entity_name]` (e.g., `slv_customers_master`)
- **Gold (Reporting):** `gld_[mart_name]_[fact_or_dim]_[entity]` (e.g., `gld_finance_fct_monthly_pnl`, `gld_sales_dim_stores`)

## 2. Microsoft Fabric & Azure Data Factory Components
- **Data Pipelines:** `pl_[source]_to_[sink]_[domain]` using snake_case (e.g., `pl_blob_to_lakehouse_inventory`).
- **Trigger Mechanisms:** `trig_[pipeline_name]_[schedule_type]` (e.g., `trig_pl_blob_to_lakehouse_inventory_daily`).

## 3. Databricks Asset Paradigms
- **Notebooks:** PascalCase indicating action and layer (e.g., `IngestBillingToBronze`, `TransformCustomersSilver`).
- **Workflows / Jobs:** UPPERCASE-KEBAB-CASE containing the run frequency (e.g., `PROD-DAILY-FINANCIAL-INGESTION`).

## 4. Technical Wiki Directory Architecture
When documenting components, the agent must output files into a strictly segregated, hierarchical directory tree rather than a flat layout. The base structure of the documentation directory is defined below:

```text
Wiki/
 ┣ 📁 solutions/           # Complex E2E setups crossing multiple technologies
 ┃ ┗ 📁 [solution_name]/   # Multi-asset folder isolated by functional project name
 ┣ 📁 pipelines/           # Standalone or shared workflow pipeline docs
 ┣ 📁 notebooks/           # Standalone processing/transformation notebooks
 ┗ 📁 databases/           # Catalog schemas, data dictionaries, and table layouts
```

## 5. File Nomenclature Within the Wiki Tree
- **Within `Wiki/solutions/[solution_name]/`:**
  * **Main Entrypoint Document:** Must use the prefix `doc_` followed by the exact solution directory name. Pattern: `doc_[solution_name].md` (e.g., `doc_financial_settlement_e2e.md`).
  * **Associated Notebooks Docs:** Pattern: `doc_nb_[notebook_name].md`.
  * **Associated Database Docs:** Pattern: `doc_db_[catalog_or_database].md`.
  * **Associated Pipeline Docs:** Pattern: `doc_pl_[pipeline_name].md`.
- **Within `Wiki/pipelines/`:**
  * Standalone pipeline summaries must match the exact asset name: `[pipeline_name].md` (e.g., `pl_blob_to_lakehouse_inventory.md`).
- **Within `Wiki/notebooks/`:**
  * Standalone notebook guides must match the exact asset name: `[notebook_name].md` (e.g., `nb_transform_slv_customers.md`).
- **Within `Wiki/databases/`:**
  * General catalog definitions must map directly to the target storage database: `[database_or_layer_name].md` (e.g., `slv_customers_master.md`).
