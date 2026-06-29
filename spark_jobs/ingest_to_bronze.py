import os
import json
from datetime import datetime
from pyspark.sql.functions import current_timestamp, lit
from spark_utils import get_spark_session

def validate_data_contract(df, table_name, data_dir):
    """
    Validates a DataFrame against a JSON schema data contract if it exists.
    """
    contract_path = os.path.join(data_dir, "../spark_jobs/contracts", f"{table_name.replace('bronze_', '')}_contract.json")
    if not os.path.exists(contract_path):
        contract_path = os.path.join(os.path.dirname(__file__), "contracts", f"{table_name.replace('bronze_', '')}_contract.json")
        
    if not os.path.exists(contract_path):
        print(f"No schema contract found for {table_name}, skipping contract audit.")
        return True
        
    print(f"Enforcing Data Contract schema verification on {table_name} using: {os.path.basename(contract_path)}")
    try:
        with open(contract_path, "r") as f:
            contract = json.load(f)
            
        required_fields = contract.get("required", [])
        properties = contract.get("properties", {})
        
        df_cols = df.columns
        for field in required_fields:
            if field not in df_cols:
                raise ValueError(f"Required field '{field}' is missing!")
                
        type_mapping = {
            "integer": ["int", "long", "bigint", "short", "integer"],
            "number": ["double", "float", "decimal", "int", "long", "bigint", "integer"],
            "string": ["string", "timestamp", "date"]
        }
        
        for field, spec in properties.items():
            if field in df_cols:
                expected_type = spec.get("type")
                spark_field = [f for f in df.schema if f.name == field][0]
                spark_type = spark_field.dataType.simpleString()
                
                if expected_type in type_mapping:
                    allowed_types = type_mapping[expected_type]
                    is_valid = any(t in spark_type for t in allowed_types)
                    if not is_valid:
                        raise TypeError(f"Column '{field}' has type '{spark_type}', but expected contract type '{expected_type}'!")
                        
        print(f"Data Contract passed successfully for {table_name}.")
        return True
    except Exception as e:
        print(f"CRITICAL: Data Contract validation failed for {table_name}: {e}")
        raise e

def ingest_file_to_bronze(spark, file_path, table_name, data_dir):
    full_path = os.path.join(data_dir, file_path)
    if not os.path.exists(full_path):
        print(f"Warning: File not found at {full_path}")
        return
        
    print(f"Ingesting {full_path} to Bronze table: {table_name}...")
    
    # Read raw CSV
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(full_path)
    
    # Enforce schema Data Contract check
    validate_data_contract(df, table_name, data_dir)
    
    # Add raw ingestion metadata (No domain-level transformations!)
    ingest_time = datetime.now()
    ingest_date_str = ingest_time.strftime("%Y-%m-%d")
    
    df_bronze = df.withColumn("ingested_at", current_timestamp()) \
                  .withColumn("source_file", lit(file_path)) \
                  .withColumn("ingest_date", lit(ingest_date_str))
                  
    # Write as Delta Table partitioned by ingest_date
    target_path = f"s3a://lakehouse/bronze/{table_name}"
    df_bronze.write.format("delta") \
        .mode("append") \
        .partitionBy("ingest_date") \
        .save(target_path)
        
    print(f"Successfully ingested {table_name} into {target_path}")

def run_bronze_ingestion():
    spark = get_spark_session("Bronze-Ingestion")
    
    # Configure directories
    # If running inside Airflow, we read from /opt/airflow/data
    # If running locally, we read from data
    data_dir = os.getenv("DATA_DIR", "data")
    
    sources = [
        ("amazon_orders.csv", "bronze_amazon_orders"),
        ("flipkart_orders.csv", "bronze_flipkart_orders"),
        ("shopify_orders.csv", "bronze_shopify_orders"),
        ("inventory.csv", "bronze_inventory"),
        ("customers.csv", "bronze_customers"),
        ("products.csv", "bronze_products")
    ]
    
    for file_name, table_name in sources:
        ingest_file_to_bronze(spark, file_name, table_name, data_dir)
        
    spark.stop()

if __name__ == "__main__":
    run_bronze_ingestion()
