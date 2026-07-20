# Candidate Resume (B.Tech CSE-AIDE)

**Name**: Madhav | **Email**: dev.madhav.hk@gmail.com | **GitHub**: [github.com/Madhavhk04](https://github.com/Madhavhk04) | **LinkedIn**: [linkedin.com/in/madhavhk04](https://linkedin.com/in/madhavhk04)  

---

## 🎯 Target Roles
**Data Engineer | Lakehouse Platform Engineer | Analytics Engineer | Big Data Software Engineer**

---

## 🛠️ Technical Core Competencies
- **Data Engineering & Lakehouse**: PySpark, Delta Lake, Apache Iceberg, Medallion Architecture, Parquet, Data Skipping, Z-Ordering, Data Contracts.
- **Orchestration & Quality**: Apache Airflow, Great Expectations, OpenLineage, Marquez, Pytest, Schema Validation.
- **Backend & Cloud Services**: FastAPI, Python 3.10+, MinIO (S3-compatible), PostgreSQL, Docker, Docker Compose, Terraform, GitHub Actions.
- **Frontend & Visualization**: React 18, Vite, Tailwind CSS, Recharts, REST APIs.

---

## 🚀 Featured Data Engineering Experience

### **Lead Data Engineer — CartCo Unified Commerce Lakehouse** *(June 2026 – July 2026)*
*5-Week B.Tech CSE-AIDE Capstone Internship Project | Live Application: [cartco-production.up.railway.app](https://cartco-production.up.railway.app)*

* **Engineered a 3-Tier Medallion Lakehouse Platform** in PySpark on top of S3-compatible MinIO object storage to consolidate fragmented sales telemetry from 5 multi-channel feeds (Shopify, Amazon, Flipkart, POS, CSV drops) for a ₹4,000 Cr GMV retailer.
* **Enforced Schema-as-Code Data Contracts** using JSON Schema boundary validation inside PySpark ingestion pipelines, eliminating downstream schema drift and automatically routing corrupted payloads to dead-letter quarantine locations.
* **Designed 4-Stage Orchestrated Data Pipelines** inside Apache Airflow utilizing Great Expectations data quality rules, ensuring 100% data constraint compliance and automated audit logging across conformed Delta Lake tables.
* **Optimized Distributed Read Performance by 80%** by implementing automated Delta Lake file compaction (`OPTIMIZE`) and multi-column **Z-Order indexing** by `customer_id` and `channel`, cutting storage fragment footprints and query execution latencies under 500ms.
* **Architected Metadata Observability and Data Lineage** using OpenLineage and Marquez APIs to enable column-level lineage tracking, exposing real-time pipeline telemetry via a FastAPI REST service and interactive React dashboard SPA.

---

## 🎓 Education

**Bachelor of Technology (B.Tech) in Computer Science & Engineering (AI & Data Engineering)**  
*Expected Graduation: May 2027*  
* **Relevant Coursework**: Distributed Systems, Big Data Analytics, Database Management Systems, Data Structures & Algorithms, Cloud Computing, Software Engineering.

---

## 📜 Certifications & Specialized Training
- **Certificate of Internship in Data Platform & Pipeline Engineering** (CartCo Unified Commerce Lakehouse, July 2026)
- **Apache Spark & Delta Lake Architecture Certification**
- **Astronomer Certified Apache Airflow DAG Authoring**
