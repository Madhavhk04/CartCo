import os
from spark_utils import get_spark_session
from dq_validator import validate_dataframe

def run_standalone_dq():
    spark = get_spark_session("Standalone-DQ-Checks")
    
    # 1. Validate Silver Orders
    try:
        print("Validating Silver Orders...")
        orders_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_orders")
        orders_rules = [
            {"type": "unique", "column": "order_id"},
            {"type": "not_null", "column": "order_id"},
            {"type": "min", "column": "total_amount", "args": {"min_value": 0.0}}
        ]
        validate_dataframe(orders_df, "silver_orders_standalone", orders_rules)
    except Exception as e:
        print(f"Error validating Silver Orders: {str(e)}")
        
    # 2. Validate Gold Customer 360
    try:
        print("Validating Gold Customer 360...")
        c360_df = spark.read.format("delta").load("s3a://lakehouse/gold/gold_customer_360")
        c360_rules = [
            {"type": "unique", "column": "customer_id"},
            {"type": "not_null", "column": "customer_id"},
            {"type": "min", "column": "lifetime_value", "args": {"min_value": 0.0}}
        ]
        validate_dataframe(c360_df, "gold_customer_360_standalone", c360_rules)
    except Exception as e:
        print(f"Error validating Gold Customer 360: {str(e)}")
        
    spark.stop()

if __name__ == "__main__":
    run_standalone_dq()
