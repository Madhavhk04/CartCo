# ADR-003: Partitioning Strategy

## Status
Approved

## Context
To prevent performance degradation as the data lake grows, we must partition files in MinIO. We need a strategy for the Bronze, Silver, and Gold medallion layers.

## Decision
1. **Bronze Layer**: Partition all tables by `ingest_date` (derived on raw landing: `YYYY-MM-DD`).
2. **Silver Layer**: Partition `silver_orders` by `channel`. Do not partition smaller reference tables (`silver_products`, `silver_customers`, `silver_inventory`) since their file sizes are small (< 10GB).
3. **Gold Layer**: Keep gold tables unpartitioned or partition daily aggregates by month/year depending on scale.

## Rationale
1. **Bronze Ingestion isolation**: Partitioning Bronze by `ingest_date` separates each daily batch run. This prevents daily ingestion runs from scanning historical files and speeds up incremental pipelines.
2. **Silver Query Optimization**: In Silver, the primary query pattern filters and aggregates orders by channel (e.g. comparing Amazon vs. Shopify performance). Partitioning by `channel` prunes files, accelerating Spark joins and dashboard queries.
3. **Over-partitioning Prevention**: Avoid partitioning tables that contain under 10GB of data. Over-partitioning causes the "small file problem" (metadata overhead and slow read performance due to multiple small parquet files).
