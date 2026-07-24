# Enterprise ANSI-SQL Development & Optimization Standards

## 1. Syntax Style & Layout Boundaries
- **Token Capitalization:** All standard ANSI-SQL structural keywords must be strictly written in uppercase (`SELECT`, `FROM`, `WHERE`, `JOIN`, `ON`, `GROUP BY`, `ORDER BY`, `COALESCE`, `MERGE`, `WHEN MATCHED`).
- **Object Reference Lowercasing:** All databases, schemas, tables, views, and columns must be strictly referenced in lowercase `snake_case`.
- **Explicit Table Aliasing:** When joining multiple tables, short and logical table aliases are mandatory (e.g., `FROM slv_sales.orders o JOIN slv_sales.customers c ON o.customer_key = c.customer_key`). Relying on implicit table prefixes or selecting un-aliased columns is strictly prohibited.
- **Common Table Expressions (CTEs):** Nested inline subqueries inside `FROM` or `JOIN` statements are completely banned. Use descriptive CTEs at the top of the script to organize processing steps linearly.

## 2. Table Mutations & Idempotence Enforcement
- **Anti-Pattern Ban:** Executing a destructive, un-logged `DELETE FROM table;` followed by a blind `INSERT INTO table;` statement is completely forbidden. This breaks transactional safety and causes storage fragmentation.
- **Atomic Upserts (MERGE INTO):** To alter target records, you must implement the `MERGE INTO` statement. The matching condition must combine partition pruning keys and high-cardinality entity identifiers to minimize transaction scan sizes:
  ```sql
  MERGE INTO slv_sales.customers AS target
  USING tmp_incoming_customers AS source
  ON target.customer_id = source.customer_id 
    AND target.processing_year = 2026 -- Enforces partition pruning
  WHEN MATCHED THEN
    UPDATE SET 
      target.customer_name = source.customer_name,
      target.email_address = source.email_address,
      target.update_timestamp = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN
    INSERT (customer_id, customer_name, email_address, processing_year, insert_timestamp, update_timestamp)
    VALUES (source.customer_id, source.customer_name, source.email_address, 2026, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
  ```

## 3. Programmable Object Architecture (SVFs, TVFs, and Stored Procedures)
In alignment with `solution_patterns/schema_ddl.md`, programmable assets must follow rigid optimization constraints:
- **Scalar-Valued Functions (SVF):** Must be deterministic, side-effect free, and heavily optimized to prevent performance degradation when applied over millions of table rows.
- **Table-Valued Functions (TVF):** Must implement explicit output column signatures to prevent breaking downstream query plans if the underlying tables undergo structural schema evolution.
- **Stored Procedures:** Must never handle raw environmental credentials. They must log operational step states internally and execute an absolute `TRY...CATCH` block that propagates errors up to the orchestration layer.
