# CartCo Technical Mock Interview Q&A Guide

This guide contains **10 detailed technical interview questions** that a Senior Data Engineer, Staff Architect, or Engineering Manager might ask about the **CartCo Unified Commerce Lakehouse**, complete with comprehensive candidate answers.

---

### Q1: Why did you choose Delta Lake over a traditional relational database (PostgreSQL) or plain Parquet files on S3?
**Candidate Answer**:  
"Plain Parquet files on S3 lack ACID transactional guarantees. If an Airflow job fails mid-write or reads happen concurrently, downstream consumers will experience partial reads or corrupted state. Furthermore, plain Parquet doesn't support update/delete operations or schema evolution without rewriting whole directories. 

While PostgreSQL handles ACID transactions, scaling a relational database to store terabytes of multi-channel e-commerce event streams becomes cost-prohibitive and slow for analytical aggregations. Delta Lake provides the best of both worlds: open-source Parquet columnar storage with ACID transaction logs (`_delta_log`), time-travel capabilities, append/merge operations, schema enforcement, and built-in Z-Ordering compaction for ultra-fast query execution."

---

### Q2: How do you handle schema drift when Amazon or Shopify alters their incoming raw order CSV structure?
**Candidate Answer**:  
"We implement a strict **Schema-as-Code Data Contract policy** at the ingestion boundary (`spark_jobs/contracts/`). When raw CSV drops land, our JSON Schema validator inspects header definitions and primitive data types prior to writing to the Bronze layer.

If an incoming feed contains unexpected columns or missing mandatory fields, the contract validator rejects the payload from entering the main pipeline and routes the corrupted batch to a dead-letter quarantine directory (`s3a://lakehouse/quarantine/`). This prevents corrupted feeds from breaking downstream Silver and Gold tables while alerting data engineering on Slack/Marquez."

---

### Q3: How do you handle duplicate orders across multi-channel feeds (e.g. Amazon retry webhook sending an order twice)?
**Candidate Answer**:  
"In the Bronze-to-Silver transformation job (`spark_jobs/bronze_to_silver_job.py`), we use PySpark window functions to de-duplicate transaction records. We define a window partitioned by `(order_id, channel)` ordered by `order_timestamp DESC`:

```python
windowSpec = Window.partitionBy("order_id", "channel").orderBy(F.col("order_date").desc())
df_dedup = df.withColumn("row_num", F.row_number().over(windowSpec)).filter("row_num = 1")
```
This ensures that only the latest, definitive state of an order is written into `silver_orders`, while maintaining idempotent pipeline re-runs."

---

### Q4: Explain the 'Small File Problem' in object storage and how your project resolves it.
**Candidate Answer**:  
"In streaming or frequent batch ingestion jobs, Spark writes thousands of tiny Parquet files (5KB–100KB) into S3. Each file requires individual S3 GET requests and metadata listings, creating severe read latency.

In CartCo, we solved this by implementing an automated compaction script (`spark_jobs/optimize_lakehouse.py`). We execute `OPTIMIZE silver_orders`, which coalesces small Parquet files into optimal ~128MB Parquet files. Additionally, we apply `VACUUM RETAIN 168 HOURS` to delete historic, unreferenced Delta log commit files older than 7 days, controlling storage costs."

---

### Q5: How does Z-Order indexing work in Delta Lake, and what columns did you pick for Z-Ordering?
**Candidate Answer**:  
"Standard partitioning organizes data into separate directory paths (e.g., `/order_date=2026-07-20/`). However, if a user queries by `customer_id` across multiple dates, Spark must perform a full scan of all partition directories.

Z-Ordering is a multi-dimensional clustering technique that uses Space-Filling Curves to map multi-column data into spatial clusters within Parquet files. We Z-Ordered `silver_orders` by `(customer_id, channel)`. When query engines run lookup queries for a specific customer or channel, Delta Lake's data skipping algorithm reads file min/max metadata statistics and skips up to 80% of unneeded Parquet files."

---

### Q6: How do you integrate Data Quality testing inside your PySpark data pipelines?
**Candidate Answer**:  
"Instead of running data quality audits after data has already reached production dashboards, we integrate **Great Expectations** assertions directly inside the PySpark pipeline before writing to Silver (`spark_jobs/dq_validator.py`).

We convert PySpark DataFrames into `SparkDFDataset` objects and execute inline expectation suites checking:
1. `expect_column_values_to_not_be_null` on primary keys (`order_id`, `sku`, `customer_id`).
2. `expect_column_values_to_be_between` on order amounts (`total_amount > 0`).
3. `expect_column_values_to_be_in_set` on channels (`Amazon`, `Flipkart`, `Shopify`, `POS`).

If an expectation suite fails beyond tolerance thresholds, the Airflow task fails immediately, preventing corrupted data propagation."

---

### Q7: How do you track data lineage and observe metadata in your platform?
**Candidate Answer**:  
"We integrated **OpenLineage** event dispatches within our PySpark utility module (`spark_utils.py`). Whenever a PySpark job executes, OpenLineage captures dataset namespaces, input source paths, output destination Delta tables, schema facets, and run IDs.

These event payloads are dispatched via HTTP to an open-source **Marquez** metadata server (`http://localhost:3000`). Our FastAPI backend queries Marquez APIs to expose a live visual column-level data lineage graph in our React UI, giving developers and auditors instant visibility from raw CSV to Gold aggregations."

---

### Q8: How does Apache Airflow orchestrate the pipeline execution DAG?
**Candidate Answer**:  
"We designed 4 modular Airflow DAGs (`dags/`):
1. `ingest_sources`: Polls source landings and runs Bronze raw ingestion.
2. `bronze_to_silver`: Executes cleaning, window deduplication, and Great Expectations checks.
3. `silver_to_gold`: Builds analytical aggregation marts (`gold_daily_revenue`, `gold_customer_360`, `gold_inventory_turnover`).
4. `data_quality_checks`: Executes daily global dataset sanity checks.

Airflow tasks use `SparkSubmitOperator` to trigger standalone PySpark execution scripts while maintaining retry mechanics and alert notification hooks."

---

### Q9: How is the FastAPI backend service designed to serve analytical metrics efficiently?
**Candidate Answer**:  
"The FastAPI backend (`dashboard-react/backend/main.py`) acts as a high-concurrency read layer between Delta Lake S3 storage and the React UI. 

To achieve sub-50ms response times, FastAPI reads pre-aggregated Gold Delta marts (`gold_daily_revenue`, `gold_customer_360`, `gold_inventory_turnover`) using PyArrow and DuckDB in-memory execution, converting analytical records directly into JSON responses without hitting full Spark clusters for UI read requests."

---

### Q10: What would you do differently if you were starting this project over with a 6-month roadmap?
**Candidate Answer**:  
"If given 6 months, I would make 3 major upgrades:
1. **Real-time Kafka Streaming**: Transition from 15-minute Airflow batch polling to Kafka event streaming with Spark Structured Streaming (`readStream`).
2. **Debezium CDC Integration**: Use Debezium to capture physical POS store transactions directly from relational WAL logs in real time.
3. **DataHub / Unity Catalog Integration**: Replace local Marquez with enterprise Unity Catalog for fine-grained role-based access control (RBAC) and automated PII data masking."
