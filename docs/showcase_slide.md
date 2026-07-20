# Executive Showcase Slide: CartCo Unified Commerce Lakehouse

---

## 🏬 CartCo Unified Commerce Lakehouse
> **A Production-Grade, Observable Medallion Lakehouse Engine for Omnichannel Retail Telemetry**

**Student Engineer**: B.Tech CSE-AIDE | **Segment**: Data Platform & Pipeline Engineering  
**Project Code**: `BTech-CSE-AIDE-2026-CartCo` | **GMV Scale**: ₹4,000+ Cr Retail Operations  

---

### 1. The Challenge & Vision
- **Problem**: 4 fragmented sales streams (Amazon, Flipkart, Shopify D2C, POS) caused severe inventory discrepancies, duplicate order accounting, and 24-hour revenue reporting latency.
- **Solution**: Built an automated 3-tier Medallion Lakehouse on Delta Lake & S3 (MinIO), enforcing schema-as-code data contracts, inline Great Expectations assertions, and OpenLineage metadata tracking.

---

### 2. System Architecture
```
[Amazon / Flipkart / Shopify / POS Feeds]
                 │ (Boundary Data Contracts)
                 ▼
    [BRONZE: Raw Delta Ingestion]
                 │ (Clean, Deduplicate & Great Expectations Checks)
                 ▼
    [SILVER: Conformed & Audited Tables]
                 │ (Window Aggregations & Z-Order Indexing)
                 ▼
    [GOLD: Daily Revenue | Customer 360 | Inventory Turnover]
                 │
                 ▼
    [FastAPI REST API] ──► [React Analytics SPA + OpenLineage Explorer]
```

---

### 3. Key Achievements & Metrics
- **⚡ 80% Faster Analytics Queries**: Optimized storage via Delta compaction (`OPTIMIZE`) and Z-Order indexing (`ZORDER BY customer_id`), cutting query response times under 500ms.
- **🛡️ 100% Quality Assurance**: Ingestion contract enforcement + Great Expectations suites eliminated downstream schema drift and isolated invalid records into quarantine buckets.
- **👁️ Full Observability**: Column-level data lineage automated using OpenLineage & Marquez.
- **🌐 100% Cloud Deployed**: Live UI on Railway ([cartco-production.up.railway.app](https://cartco-production.up.railway.app)).

---

### 4. Technology Stack
`Delta Lake` | `PySpark 3.5` | `Apache Airflow` | `MinIO` | `Great Expectations` | `OpenLineage / Marquez` | `FastAPI` | `React 18` | `Docker` | `Terraform`

---

**Live Demo**: [https://cartco-production.up.railway.app](https://cartco-production.up.railway.app) | **GitHub**: [github.com/Madhavhk04/CartCo](https://github.com/Madhavhk04/CartCo)
