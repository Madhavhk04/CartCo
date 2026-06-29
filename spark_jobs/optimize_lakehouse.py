import os
from spark_utils import get_spark_session

def optimize_delta_tables():
    print("Initiating Delta Lake Optimizations (Compaction & Vacuum)...")
    spark = get_spark_session("Optimize-Delta-Tables")
    
    # Enable bypass of SQL configuration check for vacuuming tables immediately if testing
    spark.conf.set("spark.databricks.delta.vacuum.parallelDelete.enabled", "true")
    
    tables = [
        "bronze/bronze_amazon_orders",
        "bronze/bronze_flipkart_orders",
        "bronze/bronze_shopify_orders",
        "bronze/bronze_inventory",
        "bronze/bronze_customers",
        "bronze/bronze_products",
        "silver/silver_orders",
        "silver/silver_customers",
        "silver/silver_products",
        "silver/silver_inventory",
        "gold/gold_daily_revenue",
        "gold/gold_channel_performance",
        "gold/gold_customer_360",
        "gold/gold_inventory_turnover"
    ]
    
    for table_rel_path in tables:
        path = f"s3a://lakehouse/{table_rel_path}"
        print(f"Optimizing and compacting layout for: {path}")
        
        try:
            # 1. OPTIMIZE: Merges small files to standard sizes
            # Configure Z-ORDER on high-frequency query indexes to maximize data skipping efficiency
            if "orders" in table_rel_path or "customer_360" in table_rel_path:
                print(f"Running OPTIMIZE with Z-ORDER BY customer_id for {path}")
                spark.sql(f"OPTIMIZE delta.`{path}` ZORDER BY (customer_id)")
            else:
                print(f"Running basic OPTIMIZE for {path}")
                spark.sql(f"OPTIMIZE delta.`{path}`")
                
            # 2. VACUUM: Clears parquet blocks older than retention threshold (default 7 days / 168 hours)
            # This releases storage blocks in S3 and reduces costs.
            print(f"Running VACUUM for {path}")
            spark.sql(f"VACUUM delta.`{path}`")
            print(f"Completed optimizations for: {path}")
            
        except Exception as e:
            # Fallback for local testing if running without Delta server SQL contexts
            print(f"Info: Optimization skipped or running on fallback driver for {table_rel_path}: {e}")
            
    spark.stop()

if __name__ == "__main__":
    optimize_delta_tables()
