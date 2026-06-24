# ADR-001: Table Format - Delta Lake vs Apache Iceberg

## Status
Approved

## Context
CartCo requires a transactional storage format (Lakehouse) on top of MinIO (S3-compatible storage) to support ACID transactions, time travel, schema enforcement, and high-performance upserts/deletions. We evaluated Delta Lake and Apache Iceberg.

## Decision
We selected **Delta Lake** as the storage table format.

## Rationale
1. **PySpark Integration**: Delta Lake has native, highly mature integration with Apache Spark. It does not require setting up a separate catalog server (like Nessie, Hive, or Rest Catalog) for file locking and commit coordinate management, which simplifies local deployment.
2. **Dashboard Performance**: The Rust-based Python library `deltalake` allows reading Delta tables directly into Pandas DataFrames without requiring a running JVM or Spark environment. This makes building a local, responsive Streamlit dashboard significantly faster and more resource-efficient (~50MB RAM vs 1.5GB RAM for a local Spark session).
3. **Upsert Support**: The `MERGE INTO` syntax in Delta Lake is highly optimized for merging multi-channel ingestion tables (e.g., updating refund statuses or deduplicating orders).
