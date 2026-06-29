import pytest
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from datetime import datetime

# Import transformation helper methods or define test subjects inline to test them isolatedly
def standardize_dates_pyspark(df, col_name, date_format):
    return df.withColumn("parsed_timestamp", F.to_timestamp(F.col(col_name), date_format))

def compute_order_pricing(df):
    return df.withColumn("gross_amount", F.col("quantity") * F.col("unit_price")) \
             .withColumn("net_amount", F.col("gross_amount") - F.col("discount_amount")) \
             .withColumn("total_amount", F.col("net_amount") + F.col("shipping_fee") + F.col("tax_amount"))

def deduplicate_records(df, primary_keys):
    return df.dropDuplicates(primary_keys)

def classify_inventory(df):
    return df.withColumn(
        "inventory_status",
        F.when(F.col("stock_on_hand") <= F.col("restock_threshold"), "LOW_STOCK")
         .when((F.col("quantity_sold") == 0) & (F.col("stock_on_hand") > 50), "DEAD_INVENTORY")
         .when(F.col("turnover_ratio") >= 1.5, "FAST_MOVING")
         .otherwise("HEALTHY")
    )

# 1. Unit Test: Date Parsing
def test_date_standardization(spark):
    schema = StructType([
        StructField("order_id", StringType(), True),
        StructField("amazon_date", StringType(), True),
        StructField("flipkart_date", StringType(), True),
    ])
    data = [
        ("1", "2025-02-15T10:30:00Z", "15/02/2025 10:30"),
    ]
    df = spark.createDataFrame(data, schema)
    
    # Parse Amazon
    amz_df = standardize_dates_pyspark(df, "amazon_date", "yyyy-MM-dd'T'HH:mm:ss'Z'")
    amz_parsed = amz_df.select("parsed_timestamp").collect()[0][0]
    assert isinstance(amz_parsed, datetime)
    assert amz_parsed.strftime("%Y-%m-%d %H:%M") == "2025-02-15 10:30"
    
    # Parse Flipkart
    flk_df = standardize_dates_pyspark(df, "flipkart_date", "dd/MM/yyyy HH:mm")
    flk_parsed = flk_df.select("parsed_timestamp").collect()[0][0]
    assert isinstance(flk_parsed, datetime)
    assert flk_parsed.strftime("%Y-%m-%d %H:%M") == "2025-02-15 10:30"

# 2. Unit Test: Pricing calculations
def test_compute_order_pricing(spark):
    schema = StructType([
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("discount_amount", DoubleType(), True),
        StructField("shipping_fee", DoubleType(), True),
        StructField("tax_amount", DoubleType(), True),
    ])
    data = [(2, 100.0, 10.0, 5.0, 18.0)]
    df = spark.createDataFrame(data, schema)
    res_df = compute_order_pricing(df)
    row = res_df.collect()[0]
    
    assert row["gross_amount"] == 200.0
    assert row["net_amount"] == 190.0
    assert row["total_amount"] == 213.0

# 3. Unit Test: Deduplication
def test_deduplicate_records(spark):
    schema = StructType([
        StructField("order_id", StringType(), True),
        StructField("value", StringType(), True)
    ])
    data = [
        ("1001", "first"),
        ("1001", "second"),
        ("1002", "third")
    ]
    df = spark.createDataFrame(data, schema)
    res_df = deduplicate_records(df, ["order_id"])
    assert res_df.count() == 2

# 4. Unit Test: Inventory Status Classification
def test_classify_inventory(spark):
    schema = StructType([
        StructField("product_id", StringType(), True),
        StructField("stock_on_hand", IntegerType(), True),
        StructField("restock_threshold", IntegerType(), True),
        StructField("quantity_sold", IntegerType(), True),
        StructField("turnover_ratio", DoubleType(), True),
    ])
    data = [
        ("P1", 10, 15, 5, 0.2),   # Low Stock
        ("P2", 100, 20, 0, 0.0),  # Dead Inventory
        ("P3", 200, 20, 400, 2.0), # Fast Moving
        ("P4", 50, 10, 20, 0.5)   # Healthy
    ]
    df = spark.createDataFrame(data, schema)
    res_df = classify_inventory(df)
    rows = res_df.collect()
    
    status_map = {row["product_id"]: row["inventory_status"] for row in rows}
    assert status_map["P1"] == "LOW_STOCK"
    assert status_map["P2"] == "DEAD_INVENTORY"
    assert status_map["P3"] == "FAST_MOVING"
    assert status_map["P4"] == "HEALTHY"

# 5. Unit Test: GE Parse results
def test_parse_validation_results():
    from spark_jobs.dq_validator import parse_validation_results
    
    mock_results = {
        "success": True,
        "statistics": {
            "evaluated_expectations": 2,
            "successful_expectations": 2,
            "unsuccessful_expectations": 0,
            "success_percent": 100.0
        },
        "results": [
            {
                "success": True,
                "expectation_config": {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "order_id"}
                },
                "result": {"observed_value": None}
            }
        ]
    }
    report = parse_validation_results("test_table", mock_results)
    assert report["table_name"] == "test_table"
    assert report["success"] is True
    assert report["percent_success"] == 100.0
    assert len(report["details"]) == 1
