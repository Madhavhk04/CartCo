# ADR-002: Orchestration - Apache Airflow vs Prefect

## Status
Approved

## Context
We need a robust data orchestrator to manage task dependencies, scheduling, retries, and data quality check gates. We compared Apache Airflow and Prefect.

## Decision
We chose **Apache Airflow**.

## Rationale
1. **Industry Standard**: Apache Airflow is the market leader for data engineering orchestration, with extensive community support, making the project highly recruiter-friendly for top-tier retail tech companies.
2. **Metadata & Lineage Support**: Airflow has first-class integrations with OpenLineage and Marquez. Using standard Airflow providers, metadata events are automatically emitted to Marquez without needing custom wrapper decorators around every task.
3. **Robust Scheduling**: The DAG structure enforces clear, static dependency graphs that are ideal for batch-oriented Medallion architectures.
