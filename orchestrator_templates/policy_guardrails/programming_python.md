# PySpark and Python Production Development Standards

## 1. Core Framework Boundaries
- **Native Execution Only:** Always leverage the native Spark DataFrame API or Spark SQL expressions via `pyspark.sql.functions`. 
- **Prohibited Functions:** Never use `.collect()` or `toPandas()` on non-aggregated production datasets. Use `.take(n)` or `.limit(n)` solely for metadata sampling or logging parameters.
- **Iteration Avoidance:** RDD processing and explicit `for` loops that iterate through DataFrame rows are strictly forbidden. Use vectorized column expressions via `.withColumn()`.

## 2. Idempotency and Atomic Write Operations
- **Anti-Pattern Ban:** Explicit SQL `DELETE FROM table WHERE...` followed by blind `INSERT INTO` batches within notebook cells is strictly forbidden due to risk of partial failures and log fragmentation.
- **Full Table Overwrites:** For complete snapshot tables, you must utilize atomic overwrites that clear the target directory within a single transaction:
  ```python
  df.write.mode("overwrite").format("delta").saveAsTable("catalog.schema.table")
  ```
- **Partition-Level Overwrites:** When executing incremental or partitioned loads, you must implement the `replaceWhere` option to restrict data erasure specifically to the affected boundaries:
  ```python
  df.write.mode("overwrite") \
    .option("replaceWhere", "processing_year = 2026 AND processing_month = 07") \
    .format("delta") \
    .saveAsTable("catalog.schema.table")
  ```

- **Row-Level Transactional Updates (Upserts / Merges):** When modifying specific rows within an existing target table based on incoming keys rather than overwriting full partitions, you must utilize the native Delta Lake `DeltaTable` API to execute an atomic `MERGE` operation.

- **Merge Enforcement Pattern:** Manual table re-creations or multi-step operations to simulate an upsert are strictly forbidden. You must follow the precise programmatic structure below, explicitly defining match actions for both updates and insertions:
  ```python
  from delta.tables import DeltaTable

  # 1. Instantiate the target Delta Table reference
  target_table = DeltaTable.forName(spark, "catalog.schema.target_table")

  # 2. Execute the atomic structural Upsert (Merge)
  target_table.alias("target") \
    .merge(
        source = df_incoming.alias("source"),
        condition = "target.customer_id = source.customer_id AND target.region_code = source.region_code"
    ) \
    .whenMatchedUpdate(set = {
        "target.customer_name": "source.customer_name",
        "target.last_active_date": "source.last_active_date",
        "target.update_timestamp": "current_timestamp()"
    }) \
    .whenNotMatchedInsert(values = {
        "target.customer_id": "source.customer_id",
        "target.region_code": "source.region_code",
        "target.customer_name": "source.customer_name",
        "target.last_active_date": "source.last_active_date",
        "target.insert_timestamp": "current_timestamp()",
        "target.update_timestamp": "current_timestamp()"
    }) \
    .execute()
  ```


## 3. Parametrization & Configuration Ingestion
- **Hardcoding Zero-Tolerance Policy:** Variables such as environmental paths, processing dates, target layers, or business unit parameters must never be hardcoded.
- **Orchestration Bindings:** All input parameters must be accepted at runtime using Databricks/Fabric widgets linked to parent orchestrator execution layers (ADF or Data Factory):
  ```python
  # Mandatory instantiation at notebook entry-point
  dbutils.widgets.text("processing_date", "", "Target Processing Date")
  processing_date = dbutils.widgets.get("processing_date")
  
  if not processing_date:
      raise ValueError("Critical Initialization Failure: 'processing_date' parameter is missing.")
  ```

## 4. Execution Plan Optimization
- **Explicit Broadcast Joins:** When joining a large operational dataset (e.g., transactional log) with a static dimension table under 100MB, you must wrap the smaller dataset in a `broadcast()` hint to eliminate expensive cluster shuffles:
  ```python
  from pyspark.sql.functions import broadcast
  
  df_enriched = df_large_fact.join(broadcast(df_small_dim), "customer_key", "left")
  ```

## 5. Performance and Storage Enforcement
- **Delta Lake Optimization:** Every notebook writing data to a Silver or Gold Delta table must execute an explicit `OPTIMIZE` command. If partitioned, append a `ZORDER BY` statement targeting high-cardinality predicate keys (e.g., `customer_id`, `transaction_date`).
- **Explicit Schema Enforcement:** When reading unvalidated file structures (JSON, CSV, XML), schema inference is forbidden. You must explicitly define structural boundaries using a `StructType` schema.

## 6. Robust Exception Handling Template
All major execution blocks within notebooks must be safely wrapped inside structured python try-except blocks:
```python
import sys

try:
    # Main spark transformations go here
    df_transformed = df_source.filter(df_source.is_active == True)
except Exception as e:
    error_msg = f"Execution failed in notebook step. Error details: {str(e)}"
    # Force failure visibility in Orchestration systems
    raise RuntimeError(error_msg) from e
```
