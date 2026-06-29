import os
from pyspark.sql import SparkSession

def get_spark_session(app_name="CartCo-Lakehouse"):
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    
    # Delta and Hadoop S3 packages
    packages = [
        "io.delta:delta-core_2.12:2.4.0",
        "org.apache.hadoop:hadoop-aws:3.3.4",
        "com.amazonaws:aws-java-sdk-bundle:1.12.262"
    ]
    
    builder = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", ",".join(packages)) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint) \
        .config("spark.hadoop.fs.s3a.access.key", access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.sql.warehouse.dir", "s3a://lakehouse/warehouse") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
        
    return builder.getOrCreate()
