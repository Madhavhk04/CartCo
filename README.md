# CartCo Unified Commerce Lakehouse

[![CartCo Lakehouse CI](https://github.com/cartco/lakehouse/actions/workflows/ci.yml/badge.svg)](https://github.com/cartco/lakehouse/actions/workflows/ci.yml)
[![Delta Lake](https://img.shields.io/badge/Table%20Format-Delta%20Lake-blue.svg)](https://delta.io/)
[![Orchestration](https://img.shields.io/badge/Orchestrator-Apache%20Airflow-red.svg)](https://airflow.apache.org/)
[![Observability](https://img.shields.io/badge/Metadata-OpenLineage%20%2F%20Marquez-pink.svg)](https://marquezproject.github.io/marquez/)
[![Quality](https://img.shields.io/badge/Data%20Quality-Great%20Expectations-green.svg)](https://greatexpectations.io/)

A production-grade, multi-channel retail Lakehouse architecture built for **CartCo**. This platform consolidates fragmented transaction and inventory data from **Shopify, Amazon, Flipkart, and physical retail outlets** into a standardized, audited, and observable Single Source of Truth (SSOT).

---

## Architecture & Data Flow

This platform implements a three-tier **Medallion Lakehouse Architecture** on top of MinIO (S3-compatible object storage) using Delta Lake and PySpark:

```mermaid
graph TD
    %% Source Layer
    subgraph "1. Source Data (CSV)"
        S1["amazon_orders.csv"]
        S2["flipkart_orders.csv"]
        S3["shopify_orders.csv"]
        S4["inventory.csv"]
        S5["customers.csv"]
        S6["products.csv"]
    end

    %% Bronze Layer
    subgraph "2. Bronze Layer (Raw Ingestion - Delta / MinIO)"
        B1[("bronze_amazon_orders")]
        B2[("bronze_flipkart_orders")]
        B3[("bronze_shopify_orders")]
        B4[("bronze_inventory")]
        B5[("bronze_customers")]
    end

    %% Silver Layer
    subgraph "3. Silver Layer (Standardized & Validated - Delta / MinIO)"
        S_Ord[("silver_orders")]
        S_Cust[("silver_customers")]
        S_Prod[("silver_products")]
        S_Inv[("silver_inventory")]
        GE["Great Expectations Data Quality Checks"]
    end

    %% Gold Layer
    subgraph "4. Gold Layer (Business Marts - Delta / MinIO)"
        G1[("gold_daily_revenue")]
        G2[("gold_channel_performance")]
        G3[("gold_customer_360")]
        G4[("gold_inventory_turnover")]
    end

    %% Analytics & Observability
    subgraph "5. Downstream Consumers & Monitoring"
        DB["React Dashboard (KPIs, Charts, Lineage, DQ Center)"]
        MQ["Marquez Metadata & OpenLineage UI"]
    end

    %% Ingestion Flow
    S1 --> B1
    S2 --> B2
    S3 --> B3
    S4 --> B4
    S5 --> B5

    %% Silver Processing
    B1 & B2 & B3 --> S_Ord
    B5 --> S_Cust
    B4 --> S_Inv
    S1 & S2 & S3 & B4 --> S_Prod

    %% Validation Flow
    S_Ord & S_Cust & S_Inv & S_Prod --> GE
    GE --> |Report| DB

    %% Gold Aggregations
    S_Ord --> G1
    S_Ord --> G2
    S_Ord & S_Cust --> G3
    S_Inv & S_Ord --> G4

    %% Visualizations & Lineage
    G1 & G2 & G3 & G4 --> DB
    S1 & S2 & S3 & B1 & B2 & B3 & S_Ord & G1 & G2 & G3 & G4 -.-> MQ
    MQ -.-> DB
```

1. **Bronze (Raw Ingestion)**: No-transformation raw append load from Landing to Delta tables. Partitioned by `ingest_date` (system ingestion date).
2. **Silver (Cleaned & Standardized)**: Enforces schema types, cleans up fields (e.g. email trims, name casing), normalizes multi-channel date styles, and deduplicates orders. Performs inline Great Expectations assertions.
3. **Gold (Business Aggregations)**: Aggregated analytical tables modeled for BI dashboards: `gold_daily_revenue`, `gold_channel_performance`, `gold_customer_360` (LTV, category preferences), and `gold_inventory_turnover` (turnover ratios, stagnant stock metrics).

---

## Active Services Map

| Service Name | Description | Port | Endpoint URL |
| :--- | :--- | :--- | :--- |
| **Apache Airflow** | Orchestration, scheduling, and task monitoring | `8080` | [http://localhost:8080](http://localhost:8080) |
| **MinIO Console** | Web portal for MinIO S3 object store buckets | `9001` | [http://localhost:9001](http://localhost:9001) |
| **MinIO API** | S3-compatible storage endpoints for Delta Engine | `9000` | [http://localhost:9000](http://localhost:9000) |
| **Marquez UI** | Metadata catalog and OpenLineage explorer | `3000` | [http://localhost:3000](http://localhost:3000) |
| **Marquez API** | OpenLineage tracking receiver | `5000` | [http://localhost:5000](http://localhost:5000) |
| **React Frontend** | Premium Enterprise Dashboard UI | `80` | [http://localhost](http://localhost) |
| **FastAPI Backend** | REST API Backend for Lakehouse data | `8000` | [http://localhost:8000](http://localhost:8000) |

---

## Quick Setup Instructions

Make sure you have **Docker** and **Docker Compose** installed on your system.

1. **Start all platform containers**:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d --build
   ```
   This will spin up Postgres, MinIO, Marquez, Airflow, the FastAPI backend API, and the built React frontend application.

2. **Trigger the Medallion Pipelines**:
   - Access Airflow at [http://localhost:8080](http://localhost:8080) (Credentials: `admin`/`admin`).
   - Enable the `ingest_sources` DAG and run it. The task dependencies will chain and trigger:
     - `ingest_sources` (DAG 1) -> `bronze_to_silver` (DAG 2) -> `silver_to_gold` (DAG 3) -> `data_quality_checks` (DAG 4).

3. **Explore Dashboard & Observability**:
   - Open the React Dashboard at [http://localhost](http://localhost) to view the executive overview, sales analysis, customer profiles, inventory health, platform DAG monitors, quality records, and visual lineage.
   - Open Marquez at [http://localhost:3000](http://localhost:3000) to trace dataset lineage and job durations.

### Running the Dashboard Locally (Without Docker)
For active development, you can run the dashboard services outside of Docker using local Python/Node:
1. **Start the FastAPI Backend**:
   ```bash
   cd dashboard-react/backend
   uvicorn main:app --reload --port 8000
   ```
2. **Start the React Frontend**:
   ```bash
   cd dashboard-react
   npm run dev
   ```
   Access the local hot-reloading dev server at [http://localhost:5173](http://localhost:5173).

---

## Testing Guide

The codebase has 7 tests (5 unit tests, 2 integration tests) written using pytest.

### Running Local Tests
To run tests locally, install the dependencies and execute:
```bash
pip install -r dashboard/requirements.txt pytest
pytest tests/
```
*(Ensure Java 17 JDK is installed on the host machine to allow the PySpark test fixture to initialize).*

---

## Internship Roadmap (5-Week Implementation)

### Week 1: Requirements Analysis & Docker Architecture
- Define storage topology and network mapping for MinIO, Airflow, and Marquez.
- Standardize local environment setups.
- **Milestone**: Docker Compose environment spinning up successfully.

### Week 2: Data Generation & Ingestion (Bronze)
- Implement self-contained retail dataset generator.
- Configure Spark Delta connectors to MinIO.
- Write PySpark jobs to ingest raw data into Bronze tables.
- **Milestone**: 100,000+ records successfully loaded to Bronze.

### Week 3: Cleaning, Standardisation & Data Quality (Silver)
- Standardize date parsers and clean strings.
- Deduplicate orders and handle null records.
- Integrate Great Expectations with PySpark dataset validations.
- **Milestone**: Data cleaning jobs executing and writing clean Silver records.

### Week 4: Business Intelligence Aggregations (Gold)
- Formulate window analytical functions in Spark to compute customer profiles (LTV, favored channels).
- Implement stock turnover ratios and classification metrics.
- Write scheduled Airflow DAGs.
- **Milestone**: Gold marts updated and validated.

### Week 5: Dashboard Visualization & Lineage Explorer
- Build premium dark-theme React SPA using Tailwind CSS, Recharts, and Lucide Icons.
- Design high-performance FastAPI backend API with Delta Lake S3 integration.
- Implement responsive visual layouts, interactive charts, and data lineage mapping.
- **Milestone**: Full platform visualization working, recruiter-ready presentation complete.

---

## Git Commit Recommendations

- **Feat**: Implement `data_generator.py` for multi-channel commerce simulation.
- **Docker**: Set up PostgreSQL, Airflow, and MinIO multi-service compose network.
- **Spark**: Implement Bronze ingestion job and Silver standardization pipelines.
- **Quality**: Integrate Great Expectations inline validation suite for Silver.
- **Gold**: Build analytical SQL aggregates for Customer 360 and Inventory.
- **Dashboard**: Implement Streamlit application pages for executive metrics.
- **Test**: Add unit and integration test coverage for PySpark jobs.
