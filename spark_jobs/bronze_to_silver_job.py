import os
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType, DateType, DoubleType, IntegerType
from spark_utils import get_spark_session
from dq_validator import validate_dataframe

def process_silver_products(spark):
    print("Processing Silver Products...")
    path = "s3a://lakehouse/bronze/bronze_products"
    df = spark.read.format("delta").load(path)
    
    # Deduplicate and null handle
    df_clean = df.dropDuplicates(["product_id"]) \
                 .filter(F.col("product_id").isNotNull()) \
                 .fillna({"product_name": "Unknown", "category": "General", "supplier": "Unknown"})
                 
    # Cast prices
    df_clean = df_clean.withColumn("cost_price", F.col("cost_price").cast(DoubleType())) \
                       .withColumn("retail_price", F.col("retail_price").cast(DoubleType()))
                       
    # Validate
    rules = [
        {"type": "unique", "column": "product_id"},
        {"type": "not_null", "column": "product_id"},
        {"type": "min", "column": "cost_price", "args": {"min_value": 0.0}},
        {"type": "min", "column": "retail_price", "args": {"min_value": 0.0}}
    ]
    validate_dataframe(df_clean, "silver_products", rules)
    
    # Write to Silver
    df_clean.write.format("delta").mode("overwrite").save("s3a://lakehouse/silver/silver_products")
    print("Silver Products written successfully!")

def process_silver_customers(spark):
    print("Processing Silver Customers...")
    path = "s3a://lakehouse/bronze/bronze_customers"
    df = spark.read.format("delta").load(path)
    
    # Clean email, deduplicate, filter null customer_id
    df_clean = df.dropDuplicates(["customer_id"]) \
                 .filter(F.col("customer_id").isNotNull()) \
                 .withColumn("email", F.lower(F.trim(F.col("email")))) \
                 .withColumn("signup_date", F.col("signup_date").cast(DateType())) \
                 .fillna({"first_name": "Unknown", "last_name": "Unknown", "region": "General", "country": "Unknown"})
                 
    # Validate
    rules = [
        {"type": "unique", "column": "customer_id"},
        {"type": "not_null", "column": "customer_id"}
    ]
    validate_dataframe(df_clean, "silver_customers", rules)
    
    # Write to Silver
    df_clean.write.format("delta").mode("overwrite").save("s3a://lakehouse/silver/silver_customers")
    print("Silver Customers written successfully!")

def process_silver_inventory(spark):
    print("Processing Silver Inventory...")
    path = "s3a://lakehouse/bronze/bronze_inventory"
    df = spark.read.format("delta").load(path)
    
    # Deduplicate, cast
    df_clean = df.dropDuplicates(["product_id"]) \
                 .filter(F.col("product_id").isNotNull()) \
                 .withColumn("stock_on_hand", F.col("stock_on_hand").cast(IntegerType())) \
                 .withColumn("reserved_stock", F.col("reserved_stock").cast(IntegerType())) \
                 .withColumn("restock_threshold", F.col("restock_threshold").cast(IntegerType())) \
                 .withColumn("last_updated", F.to_timestamp(F.col("last_updated"), "yyyy-MM-dd HH:mm:ss"))
                 
    # Validate
    rules = [
        {"type": "not_null", "column": "product_id"},
        {"type": "min", "column": "stock_on_hand", "args": {"min_value": 0}}
    ]
    validate_dataframe(df_clean, "silver_inventory", rules)
    
    # Write to Silver
    df_clean.write.format("delta").mode("overwrite").save("s3a://lakehouse/silver/silver_inventory")
    print("Silver Inventory written successfully!")

def process_silver_orders(spark):
    print("Processing Silver Orders (Shopify, Amazon, Flipkart)...")
    
    # 1. Shopify
    sh_df = spark.read.format("delta").load("s3a://lakehouse/bronze/bronze_shopify_orders")
    sh_aligned = sh_df.select(
        F.col("order_id").cast("string").alias("order_id"),
        F.col("customer_id").cast("string").alias("customer_id"),
        F.col("product_id").cast("string").alias("product_id"),
        F.to_timestamp(F.col("order_date"), "yyyy-MM-dd HH:mm:ss").alias("order_timestamp"),
        F.col("quantity").cast(IntegerType()).alias("quantity"),
        F.col("unit_price").cast(DoubleType()).alias("unit_price"),
        F.col("discount").cast(DoubleType()).alias("discount_amount"),
        F.col("shipping_fee").cast(DoubleType()).alias("shipping_fee"),
        F.col("taxes").cast(DoubleType()).alias("tax_amount"),
        F.lit("SHOPIFY").alias("channel"),
        F.upper(F.col("payment_method")).alias("payment_method"),
        F.when(F.col("refund_flag") == 1, "REFUNDED")
         .when(F.col("fulfillment_status") == "cancelled", "CANCELLED")
         .otherwise("COMPLETED").alias("order_status")
    )

    # 2. Amazon
    amz_df = spark.read.format("delta").load("s3a://lakehouse/bronze/bronze_amazon_orders")
    # Date parsing: 2025-02-01T12:00:00Z -> Timestamp
    amz_aligned = amz_df.select(
        F.col("amazon_order_id").cast("string").alias("order_id"),
        F.col("customer_id").cast("string").alias("customer_id"),
        F.col("product_id").cast("string").alias("product_id"),
        F.to_timestamp(F.col("purchase_date"), "yyyy-MM-dd'T'HH:mm:ss'Z'").alias("order_timestamp"),
        F.col("quantity").cast(IntegerType()).alias("quantity"),
        F.col("item_price").cast(DoubleType()).alias("unit_price"),
        F.lit(0.0).cast(DoubleType()).alias("discount_amount"),
        F.col("shipping_price").cast(DoubleType()).alias("shipping_fee"),
        F.col("item_tax").cast(DoubleType()).alias("tax_amount"),
        F.lit("AMAZON").alias("channel"),
        F.lit("PREPAID").alias("payment_method"),
        F.lit("COMPLETED").alias("order_status")
    )

    # 3. Flipkart
    flk_df = spark.read.format("delta").load("s3a://lakehouse/bronze/bronze_flipkart_orders")
    # Date parsing: 01/02/2025 12:00 -> Timestamp
    flk_aligned = flk_df.select(
        F.col("flipkart_order_id").cast("string").alias("order_id"),
        F.col("customer_id").cast("string").alias("customer_id"),
        F.col("product_id").cast("string").alias("product_id"),
        F.to_timestamp(F.col("order_timestamp"), "dd/MM/yyyy HH:mm").alias("order_timestamp"),
        F.col("qty").cast(IntegerType()).alias("quantity"),
        F.col("price_per_unit").cast(DoubleType()).alias("unit_price"),
        # Calculate discount amount from percent
        (F.col("qty") * F.col("price_per_unit") * (F.col("discount_percent") / 100.0)).cast(DoubleType()).alias("discount_amount"),
        F.col("delivery_charges").cast(DoubleType()).alias("shipping_fee"),
        F.lit(0.0).cast(DoubleType()).alias("tax_amount"), # Calculated below for consistency
        F.lit("FLIPKART").alias("channel"),
        F.upper(F.col("payment_type")).alias("payment_method"),
        F.when(F.col("order_status") == "Returned", "RETURNED")
         .when(F.col("order_status") == "Cancelled", "CANCELLED")
         .otherwise("COMPLETED").alias("order_status")
    )
    # Estimate standard GST for Flipkart (e.g., 12%)
    flk_aligned = flk_aligned.withColumn("tax_amount", ((F.col("quantity") * F.col("unit_price") - F.col("discount_amount")) * 0.12).cast(DoubleType()))

    # Union all sales channels
    union_df = sh_aligned.unionByName(amz_aligned).unionByName(flk_aligned)
    
    # Calculate amounts
    orders_df = union_df.withColumn("gross_amount", F.col("quantity") * F.col("unit_price")) \
                        .withColumn("net_amount", F.col("gross_amount") - F.col("discount_amount")) \
                        .withColumn("total_amount", F.col("net_amount") + F.col("shipping_fee") + F.col("tax_amount"))
                        
    # Deduplicate and null filter
    orders_clean = orders_df.dropDuplicates(["order_id"]) \
                            .filter(F.col("order_id").isNotNull()) \
                            .filter(F.col("customer_id").isNotNull()) \
                            .filter(F.col("product_id").isNotNull())
                            
    # Validate
    rules = [
        {"type": "unique", "column": "order_id"},
        {"type": "not_null", "column": "order_id"},
        {"type": "min", "column": "total_amount", "args": {"min_value": 0.0}},
        {"type": "set", "column": "channel", "args": {"value_set": ["SHOPIFY", "AMAZON", "FLIPKART", "PHYSICAL_STORE"]}}
    ]
    validate_dataframe(orders_clean, "silver_orders", rules)
    
    # Write to Silver Delta Table
    orders_clean.write.format("delta").mode("overwrite").save("s3a://lakehouse/silver/silver_orders")
    print("Silver Orders written successfully!")

def run_silver_pipeline():
    spark = get_spark_session("Bronze-to-Silver-Job")
    
    process_silver_products(spark)
    process_silver_customers(spark)
    process_silver_inventory(spark)
    process_silver_orders(spark)
    
    spark.stop()

if __name__ == "__main__":
    run_silver_pipeline()
