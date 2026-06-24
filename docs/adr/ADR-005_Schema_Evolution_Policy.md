# ADR-005: Schema Evolution Policy

## Status
Approved

## Context
As upstream systems change (e.g. Shopify or Amazon adding new checkout columns), our pipeline must handle schema adjustments. We need a clear evolution policy for Silver (clean repository) and Gold (business marts) tables.

## Decision
1. **Silver Layer (Schema Enforcement)**: Enforce strict schema constraints. Any schema modifications must fail the pipeline, prompting manual inspection and versioning.
2. **Gold Layer (Schema Evolution)**: Enable schema evolution using Delta Lake's auto-merge feature (`spark.databricks.delta.schema.autoMerge.enabled = true`).

## Rationale
1. **Silver Integrity**: The Silver layer represents the cleaned, standardized source of truth for the entire enterprise. Undetected schema drift (such as a column data type change or drop) can corrupt downstream financial aggregates. Strict schema enforcement protects data consistency.
2. **Gold Business Flexibility**: Gold marts are consumer-facing aggregated datasets. When new business metrics or attributes are added to Silver, they should flow into Gold dynamically without requiring table drops or manual rebuilds. Auto-merge allows Delta to safely append new columns to existing schemas.
