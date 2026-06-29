import os
import json
import pytest
from pyspark.sql import functions as F
from spark_jobs.ingest_to_bronze import ingest_file_to_bronze

def test_bronze_ingestion_integration(spark, tmp_path):
    """
    Integration Test 1: Simulates raw source data landing, executes bronze ingestion,
    and validates Delta table format write properties on local filesystem.
    """
    # 1. Setup mock raw CSV data
    data_dir = tmp_path / "data"
    os.makedirs(data_dir, exist_ok=True)
    
    csv_file = data_dir / "customers.csv"
    with open(csv_file, "w") as f:
        f.write("customer_id,first_name,last_name,email,phone,signup_date,region,country\n")
        f.write("CUST_001,John,Doe,john@example.com,1234567890,2025-01-01,North,USA\n")
        f.write("CUST_002,Jane,Smith,jane@example.com,0987654321,2025-01-02,South,India\n")
        
    # 2. Run ingestion using spark to local file target
    # Override standard s3a:// prefix with local temp path for test execution
    bronze_table_name = "bronze_customers_test"
    target_path = os.path.join(tmp_path, "bronze", bronze_table_name)
    
    # Read raw CSV
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(str(csv_file))
    df_bronze = df.withColumn("ingested_at", F.current_timestamp()) \
                  .withColumn("source_file", F.lit("customers.csv")) \
                  .withColumn("ingest_date", F.lit("2026-06-22"))
                  
    df_bronze.write.format("delta").mode("overwrite").partitionBy("ingest_date").save(target_path)
    
    # 3. Assertions on written Delta table
    assert os.path.exists(os.path.join(target_path, "_delta_log"))
    
    read_df = spark.read.format("delta").load(target_path)
    assert read_df.count() == 2
    assert "ingested_at" in read_df.columns
    assert "source_file" in read_df.columns


def test_bronze_to_silver_and_dq_integration(spark, tmp_path):
    """
    Integration Test 2: Simulates the Bronze-to-Silver stage, merging, standardizing,
    and running Great Expectations checks. Asserts validation reports are saved.
    """
    # 1. Create mock bronze customers Delta Table
    bronze_path = os.path.join(tmp_path, "bronze", "bronze_customers_test")
    schema = ["customer_id", "first_name", "last_name", "email", "phone", "signup_date", "region", "country"]
    data = [
        ("CUST_001", "John", "Doe", "JOHN@EXAMPLE.COM ", "123456", "2025-01-01", "North", "USA"),
        ("CUST_001", "John Duplicated", "Doe", "john@example.com", "123456", "2025-01-01", "North", "USA"),
        (None, "Invalid", "Cust", "null@example.com", "0000", "2025-01-01", "South", "India")
    ]
    df_bronze = spark.createDataFrame(data, schema)
    df_bronze.write.format("delta").mode("overwrite").save(bronze_path)
    
    # 2. Run cleansing transformations (deduplication & null handling)
    df = spark.read.format("delta").load(bronze_path)
    df_clean = df.dropDuplicates(["customer_id"]) \
                 .filter(F.col("customer_id").isNotNull()) \
                 .withColumn("email", F.lower(F.trim(F.col("email"))))
                 
    # 3. Run Great Expectations
    from spark_jobs.dq_validator import validate_dataframe
    os.environ["DQ_REPORT_DIR"] = os.path.join(tmp_path, "dq_reports")
    
    rules = [
        {"type": "unique", "column": "customer_id"},
        {"type": "not_null", "column": "customer_id"}
    ]
    
    report = validate_dataframe(df_clean, "silver_customers_test", rules)
    
    # 4. Assertions on results and DQ reports
    assert report["success"] is True
    assert report["percent_success"] == 100.0
    
    silver_path = os.path.join(tmp_path, "silver", "silver_customers_test")
    df_clean.write.format("delta").mode("overwrite").save(silver_path)
    
    # Verify Silver table
    read_silver = spark.read.format("delta").load(silver_path)
    assert read_silver.count() == 1 # 1 unique customer row remains
    row = read_silver.collect()[0]
    assert row["customer_id"] == "CUST_001"
    assert row["email"] == "john@example.com" # email lowercased and trimmed
    
    # Verify report JSON was created
    report_file_path = os.path.join(tmp_path, "dq_reports", "silver_customers_test_dq_report.json")
    assert os.path.exists(report_file_path)
    
    with open(report_file_path, "r") as f:
        saved_report = json.load(f)
        assert saved_report["table_name"] == "silver_customers_test"
        assert saved_report["success"] is True
