# ADR-006: Ingestion Tool Selection (Custom Python with Spark vs Airbyte vs Kafka Connect)

## Status
Approved

## Context
CartCo operates as a multi-channel retailer processing ₹4,000 Cr in GMV across Shopify, Amazon, Flipkart, in-store POS systems, and physical distributor CSV drop directories. To feed our Medallion Lakehouse layout in MinIO (S3), we need to select the ingestion tool pattern.

We evaluated three options:
1. **Airbyte**: An open-source ELT data integration tool.
2. **Kafka Connect**: A framework for connecting Kafka broker pipelines to external storage/databases.
3. **Custom Python Ingestion with Spark connectors**: Custom-written Python scripts triggering PySpark reader/writer modules.

## Decision
We selected **Custom Python Ingestors leveraging PySpark S3/Delta drivers** as the primary ingestion framework for the batch CSV drops and API feeds, while establishing Kafka for simulated streaming.

## Consequences
* **Pros**:
  * **Unified Compute Engine**: Using PySpark directly for both ingestion (Landing-to-Bronze) and processing (Bronze-to-Silver) prevents tooling bloat, using the same Spark driver config for the whole medallion flow.
  * **Lightweight Footprint**: Custom Python scripts avoid the high overhead of running an Airbyte server or Kafka Connect cluster locally under Docker Compose, saving RAM and CPU.
  * **Direct Schema Control**: Simplifies checking custom Data Contracts (schema-as-code validation) directly inside the python wrapper before writing Delta table parquet blocks.
* **Cons**:
  * We lose out-of-the-box UI features provided by Airbyte for sync tracking. We mitigate this by using Airflow task logging and Marquez Observability.
