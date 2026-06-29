import os
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from spark_utils import get_spark_session

def process_gold_daily_revenue(spark):
    print("Generating Gold Daily Revenue...")
    orders_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_orders")
    
    # Filter out cancelled orders for revenue reporting
    valid_orders = orders_df.filter(F.col("order_status") != "CANCELLED")
    
    daily_revenue = valid_orders.withColumn("order_date", F.to_date(F.col("order_timestamp"))) \
        .groupBy("order_date") \
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.countDistinct("customer_id").alias("active_customers"),
            F.round(F.sum("gross_amount"), 2).alias("gross_revenue"),
            F.round(F.sum("discount_amount"), 2).alias("total_discounts"),
            F.round(F.sum("shipping_fee"), 2).alias("total_shipping"),
            F.round(F.sum("tax_amount"), 2).alias("total_taxes"),
            F.round(F.sum("net_amount"), 2).alias("net_revenue"),
            F.round(F.sum("total_amount"), 2).alias("total_revenue"),
            # Refunds tracking
            F.round(F.sum(F.when(F.col("order_status") == "REFUNDED", F.col("net_amount")).otherwise(0.0)), 2).alias("total_refunds")
        ) \
        .sort(F.col("order_date").desc())
        
    daily_revenue.write.format("delta").mode("overwrite").save("s3a://lakehouse/gold/gold_daily_revenue")
    print("Gold Daily Revenue written successfully!")

def process_gold_channel_performance(spark):
    print("Generating Gold Channel Performance...")
    orders_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_orders")
    
    channel_perf = orders_df.groupBy("channel") \
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.countDistinct("customer_id").alias("unique_customers"),
            F.round(F.sum(F.when(F.col("order_status") != "CANCELLED", F.col("total_amount")).otherwise(0.0)), 2).alias("total_revenue"),
            F.round(F.avg(F.when(F.col("order_status") != "CANCELLED", F.col("total_amount"))), 2).alias("average_order_value"),
            # Cancellation rate
            F.round(F.count(F.when(F.col("order_status") == "CANCELLED", 1)) / F.count("order_id") * 100.0, 2).alias("cancellation_rate_percent"),
            # Refund rate
            F.round(F.count(F.when(F.col("order_status") == "REFUNDED", 1)) / F.count("order_id") * 100.0, 2).alias("refund_rate_percent")
        )
        
    channel_perf.write.format("delta").mode("overwrite").save("s3a://lakehouse/gold/gold_channel_performance")
    print("Gold Channel Performance written successfully!")

def process_gold_customer_360(spark):
    print("Generating Gold Customer 360...")
    orders_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_orders")
    customers_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_customers")
    products_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_products")
    
    # 1. Base order aggregations per customer
    customer_orders = orders_df.filter(F.col("order_status") != "CANCELLED") \
        .groupBy("customer_id") \
        .agg(
            F.round(F.sum("total_amount"), 2).alias("lifetime_value"),
            F.countDistinct("order_id").alias("total_orders"),
            F.min("order_timestamp").alias("first_purchase"),
            F.max("order_timestamp").alias("last_purchase")
        )
        
    # 2. Preferred channel (window function over channel counts)
    channel_counts = orders_df.groupBy("customer_id", "channel") \
        .agg(F.count("order_id").alias("ch_order_count"))
    
    w_ch = Window.partitionBy("customer_id").orderBy(F.col("ch_order_count").desc(), F.col("channel"))
    pref_channel = channel_counts.withColumn("rn", F.row_number().over(w_ch)) \
        .filter(F.col("rn") == 1) \
        .select("customer_id", F.col("channel").alias("preferred_channel"))
        
    # 3. Favorite product category (join products to orders, then window)
    order_products = orders_df.join(products_df, "product_id", "inner")
    category_counts = order_products.groupBy("customer_id", "category") \
        .agg(F.count("order_id").alias("cat_order_count"))
        
    w_cat = Window.partitionBy("customer_id").orderBy(F.col("cat_order_count").desc(), F.col("category"))
    pref_category = category_counts.withColumn("rn", F.row_number().over(w_cat)) \
        .filter(F.col("rn") == 1) \
        .select("customer_id", F.col("category").alias("favorite_category"))
        
    # 4. Join all together with silver_customers info
    customer_360 = customers_df \
        .join(customer_orders, "customer_id", "left") \
        .join(pref_channel, "customer_id", "left") \
        .join(pref_category, "customer_id", "left") \
        .fillna({
            "lifetime_value": 0.0,
            "total_orders": 0,
            "preferred_channel": "None",
            "favorite_category": "None"
        })
        
    customer_360.write.format("delta").mode("overwrite").save("s3a://lakehouse/gold/gold_customer_360")
    print("Gold Customer 360 written successfully!")

def process_gold_inventory_turnover(spark):
    print("Generating Gold Inventory Turnover...")
    orders_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_orders")
    products_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_products")
    inventory_df = spark.read.format("delta").load("s3a://lakehouse/silver/silver_inventory")
    
    # 1. Product sales aggregation (last 365 days / all orders)
    product_sales = orders_df.filter(F.col("order_status") == "COMPLETED") \
        .groupBy("product_id") \
        .agg(
            F.sum("quantity").alias("quantity_sold"),
            F.round(F.sum("net_amount"), 2).alias("sales_revenue")
        )
        
    # 2. Join products, inventory, and sales
    # Drop metadata columns to prevent duplicate column names on join
    products_clean = products_df.drop("ingested_at", "ingest_date", "source_file")
    inventory_clean = inventory_df.drop("ingested_at", "ingest_date", "source_file")
    
    turnover = products_clean.join(inventory_clean, "product_id", "inner") \
        .join(product_sales, "product_id", "left") \
        .fillna({"quantity_sold": 0, "sales_revenue": 0.0})
        
    # 3. Calculate COGS and Turnover Ratio
    # COGS = quantity_sold * cost_price
    # Average inventory value = stock_on_hand * cost_price
    # Turnover ratio = COGS / (Average inventory value)
    turnover = turnover.withColumn("cogs", F.round(F.col("quantity_sold") * F.col("cost_price"), 2)) \
                       .withColumn("current_inventory_value", F.round(F.col("stock_on_hand") * F.col("cost_price"), 2)) \
                       .withColumn("turnover_ratio", F.round(F.col("cogs") / (F.col("current_inventory_value") + 1.0), 4))
                       
    # 4. Classify Inventory Status & Stock Health
    turnover = turnover.withColumn(
        "inventory_status",
        F.when(F.col("stock_on_hand") <= F.col("restock_threshold"), "LOW_STOCK")
         .when((F.col("quantity_sold") == 0) & (F.col("stock_on_hand") > 50), "DEAD_INVENTORY")
         .when(F.col("turnover_ratio") >= 1.5, "FAST_MOVING")
         .otherwise("HEALTHY")
    )
    
    turnover.write.format("delta").mode("overwrite").save("s3a://lakehouse/gold/gold_inventory_turnover")
    print("Gold Inventory Turnover written successfully!")

def run_gold_pipeline():
    spark = get_spark_session("Silver-to-Gold-Job")
    
    process_gold_daily_revenue(spark)
    process_gold_channel_performance(spark)
    process_gold_customer_360(spark)
    process_gold_inventory_turnover(spark)
    
    spark.stop()

if __name__ == "__main__":
    run_gold_pipeline()
