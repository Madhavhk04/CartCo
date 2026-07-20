# CartCo Multi-Channel Data Layer Specification

## 1. Overview & Data Sources

The **CartCo Unified Commerce Lakehouse** ingests telemetry from 6 distinct operational streams representing multi-channel retail operations across India generating over ₹4,000 Cr in gross merchandise value (GMV):

1. **`amazon_orders.csv`**: Transaction feeds from Amazon India seller platform.
2. **`flipkart_orders.csv`**: Order telemetry from Flipkart seller portal.
3. **`shopify_orders.csv`**: Direct-to-Consumer (D2C) web application order logs.
4. **`inventory.csv`**: Centralized fulfillment center stock snapshots across 5 regional warehouses (BOM, DEL, BLR, MAA, CCU).
5. **`customers.csv`**: Master Customer Relationship Management (CRM) record exports.
6. **`products.csv`**: Universal Stock Keeping Unit (SKU) product catalog.

---

## 2. Medallion Layer Schema Definitions

### 2.1 Bronze Layer (Raw Storage)
- **Format**: Delta Lake (`s3a://lakehouse/bronze/`)
- **Partitioning**: `ingest_date` (Format: `YYYY-MM-DD`)
- **Policy**: Raw append-only ingestion with schema validation at boundary via Data Contracts (`spark_jobs/contracts/`).
- **Fields Preserved**: Original payload strings, source channel flags, `_ingest_timestamp`.

### 2.2 Silver Layer (Cleaned & Standardized)
- **Format**: Delta Lake (`s3a://lakehouse/silver/`)
- **Partitioning**: `order_date` or `snapshot_date`
- **Cleansing Rules**:
  - **Date Normalization**: All incoming channel timestamps parsed to UTC ISO-8601 (`YYYY-MM-DD HH:mm:ss`).
  - **String Standardization**: Lowercase email trimming, uppercase SKU normalization.
  - **De-duplication**: Order IDs deduplicated across multi-channel feeds using window functions partitioned by `(order_id, channel)` ordered by `order_timestamp DESC`.
  - **Quarantine**: Anomalous records (e.g. `amount <= 0`, missing customer references) routed to `s3a://lakehouse/quarantine/`.

#### Silver Schema: `silver_orders`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | `StringType` | NOT NULL | Standardized universal order identifier |
| `channel` | `StringType` | Enum (Amazon, Flipkart, Shopify, POS) | Sales channel name |
| `customer_id` | `StringType` | NOT NULL | Universal customer identifier |
| `order_date` | `TimestampType` | NOT NULL | Transaction timestamp in UTC |
| `total_amount` | `DoubleType` | `> 0` | Gross order value in INR (₹) |
| `order_status` | `StringType` | Enum (COMPLETED, SHIPPED, CANCELLED, RETURNED) | Order fulfillment state |
| `item_count` | `IntegerType` | `>= 1` | Total units ordered |
| `ingest_date` | `StringType` | `YYYY-MM-DD` | Ingestion partition key |

---

### 2.3 Gold Layer (Business Marts)
- **Format**: Delta Lake (`s3a://lakehouse/gold/`)
- **Aggregations**:

#### 1. `gold_daily_revenue`
- **Fields**: `date`, `channel`, `total_revenue`, `order_count`, `avg_order_value`, `returned_order_count`
- **Purpose**: Power revenue trends, daily run-rate, and return impact widgets.

#### 2. `gold_channel_performance`
- **Fields**: `channel`, `total_sales`, `channel_share_pct`, `conversion_count`, `cancellation_rate`
- **Purpose**: Multi-channel attribution and channel comparison charts.

#### 3. `gold_customer_360`
- **Fields**: `customer_id`, `customer_name`, `email`, `total_lifetime_value`, `order_frequency`, `favorite_channel`, `last_order_date`, `customer_segment` (VIP, Regular, At-Risk)
- **Purpose**: Customer lifetime value analytics and churn risk segmentation.

#### 4. `gold_inventory_turnover`
- **Fields**: `sku`, `product_name`, `category`, `current_stock`, `reorder_level`, `turnover_ratio`, `stock_status` (HEALTHY, LOW_STOCK, OUT_OF_STOCK, STAGNANT)
- **Purpose**: Stockout prevention, reorder triggering, and warehouse optimization.

---

## 3. Data Contracts & Data Quality Enforcement

All raw CSV streams pass through explicit JSON schema data contracts defined in `spark_jobs/contracts/`:
- Contract schema validation verifies required columns and primitive data types prior to writing to Bronze.
- Silver ingestion executes inline **Great Expectations** data assertions (`spark_jobs/dq_validator.py`):
  1. `expect_column_values_to_not_be_null` on primary keys (`order_id`, `customer_id`, `sku`).
  2. `expect_column_values_to_be_between` on financial metrics (`total_amount > 0`).
  3. `expect_column_values_to_be_in_set` on status enumerations.
  4. `expect_table_row_count_to_be_between` for data completeness.

---

## 4. Synthetic Data Generation

The synthetic dataset generator script [`spark_jobs/data_generator.py`](../spark_jobs/data_generator.py) produces realistic omnichannel telemetry:
- **Volume**: 100,000+ transaction records spanning 365 rolling days.
- **Realistic Noise**: Injects 2% date format mismatches, duplicate order retries, and casing variations to thoroughly exercise cleansing and quarantine routines.
- **License**: Creative Commons Zero (CC0) / Open Data License for public testing and recruitment evaluation.
