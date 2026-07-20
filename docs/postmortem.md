# Engineering Incident Postmortem: PySpark Delta Classpath Resolution & Schema Contract Validation

**Incident Reference**: INC-2026-07-01  
**Severity**: Medium (Development Blocker)  
**Status**: Resolved & Prevented  
**Affected Components**: `spark_jobs/bronze_to_silver_job.py`, CI Pipeline (`.github/workflows/ci.yml`), `tests/conftest.py`  

---

## 1. Executive Summary

During initial integration testing of the PySpark Bronze-to-Silver transformation job, test execution failed systematically with `ClassNotFoundException: io.delta.sql.DeltaSparkSessionExtension` in pytest sessions and GitHub Actions CI runs. Simultaneously, incoming multi-channel order feeds containing null string variations (`"NULL"`, `"N/A"`, `""`) bypassed primitive JSON Schema validation checks, causing silent failures during Silver table datetime casting.

Both issues were diagnosed, resolved, and documented with preventive regression tests added to the CI test suite.

---

## 2. Incident Timeline

| Date / Time | Event Description |
| :--- | :--- |
| **July 1, 10:15 AM** | First end-to-end pytest run executed against `test_spark_jobs.py`. |
| **July 1, 10:18 AM** | Test suite failed with `Py4JJavaError: ClassNotFoundException: io.delta.sql.DeltaSparkSessionExtension`. |
| **July 1, 11:30 AM** | Diagnosed missing `delta-spark` package configurations in local PySpark session initialization (`conftest.py`). |
| **July 1, 01:45 PM** | Added `spark.jars.packages` to Spark session builder, resolving Delta JAR classpath loading. |
| **July 1, 03:20 PM** | Secondary bug identified: Multi-channel orders containing `"N/A"` email strings passed JSON Schema string checks but failed PySpark timestamp casting (`order_date`), writing null timestamps to Silver. |
| **July 1, 05:00 PM** | Enforced string trimming and regex normalization inside `spark_jobs/contracts/` and added Great Expectations non-null assertions. |
| **July 1, 06:15 PM** | All 12 automated unit & integration tests passed cleanly in local environment and GitHub Actions CI. |

---

## 3. Root Cause Analysis (RCA)

### RCA 1: PySpark Delta JAR Classpath Omission
The PySpark session builder in `tests/conftest.py` initialized a standard Spark session without configuring the Delta Lake extension JAR packages:
```python
# ❌ INCORRECT (Missing Delta JAR packages):
spark = SparkSession.builder.appName("Test").getOrCreate()
```
When Spark attempted to execute Delta table format commands (`FORMAT delta`), the underlying JVM ClassLoader failed to locate `io.delta.sql.DeltaSparkSessionExtension`, raising a fatal Java ClassNotFound exception.

### RCA 2: Implicit Null Variations in CSV Drops
The JSON Schema data contract checked `type: string` for order dates and customer emails. However, raw CSV drops from Amazon and Shopify contained literal string variations such as `"N/A"`, `"null"`, and `" "` (whitespace). Because these were valid JSON strings, they passed boundary contract checks, but evaluating `to_timestamp()` in PySpark produced `NULL` timestamps, corrupting Silver partition keys.

---

## 4. Resolution & Fixes Applied

### Fix 1: Configure Delta Lake Extensions in PySpark Session Builder
Updated `tests/conftest.py` and `spark_utils.py` to automatically download and bind Delta Lake 3.x JAR dependencies:

```python
# ✅ CORRECT (Delta Lake JAR packages configured):
from delta import configure_with_catalogs
from pyspark.sql import SparkSession

builder = SparkSession.builder \
    .appName("CartCo-Lakehouse") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_with_catalogs(builder).getOrCreate()
```

### Fix 2: Null Sanitization & Great Expectations Assertions
Enhanced string normalization inside `spark_jobs/bronze_to_silver_job.py` to replace literal null strings (`"N/A"`, `"NULL"`, `""`) with `null` SQL primitives before datetime parsing, combined with Great Expectations non-null validation:

```python
# Standardize literal null string representations
null_literals = ["N/A", "NULL", "null", ""]
df_clean = df.withColumn(
    "order_date_clean",
    F.when(F.trim(F.col("order_date")).isin(null_literals), None)
     .otherwise(F.col("order_date"))
)
```

---

## 5. Preventive Measures & Lessons Learned

1. **Automated Package Injection**: Configured `.github/workflows/ci.yml` to pre-cache Delta Lake dependencies and set `PYSPARK_SUBMIT_ARGS="--packages io.delta:delta-spark_2.12:3.1.0 pyspark-shell"`.
2. **Regression Test Suite**: Added explicit unit test `TEST-SPK-05` in `tests/test_spark_jobs.py` to verify that corrupt dates and null strings are properly quarantined.
3. **Observability Alerts**: Added logging hooks to dispatch quarantine alerts to Marquez when invalid row counts exceed 1% of batch volume.
