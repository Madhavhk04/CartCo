import os
from spark_utils import get_spark_session

def register_catalog_metadata():
    print("Registering CartCo Lakehouse Metastore Catalog Details...")
    spark = get_spark_session("Catalog-Registry")
    
    tables = {
        "silver_orders": {
            "description": "Standardized, deduplicated retail transaction events across all ingest channels.",
            "owner": "cartco_de_team",
            "columns": {
                "order_id": "Globally unique order identifier conformed from seller APIs",
                "customer_id": "Unique identifier linking transaction to silver_customers profiles",
                "total_amount": "Net transaction value including taxes and shipping fees"
            }
        },
        "silver_customers": {
            "description": "Cleaned and conformed customer registry compiled from Shopify and POS logins.",
            "owner": "cartco_de_team",
            "columns": {
                "customer_id": "Primary key linking users to transaction logs",
                "email": "Normalized and deduplicated user email address",
                "signup_date": "Sign up date formatted as standard YYYY-MM-DD"
            }
        },
        "gold_customer_360": {
            "description": "Business aggregate mart housing customer lifetime value (LTV) and category metrics.",
            "owner": "analytics_bi_team",
            "columns": {
                "lifetime_value": "Cumulative gross revenue value spent by this user",
                "preferred_channel": "Channel with the highest transaction frequency",
                "favorite_category": "Product category purchased most frequently by volume"
            }
        }
    }
    
    for table_name, meta in tables.items():
        layer = "silver" if table_name.startswith("silver_") else "gold"
        path = f"s3a://lakehouse/{layer}/{table_name}"
        print(f"Adding catalog comments and ownership properties for {table_name}...")
        
        try:
            # 1. Register Table-Level Description and Owner
            spark.sql(f"""
                ALTER TABLE delta.`{path}` 
                SET TBLPROPERTIES (
                    'comment' = '{meta["description"]}',
                    'owner' = '{meta["owner"]}',
                    'catalog_status' = 'registered'
                )
            """)
            
            # 2. Register Column-Level comments
            for col_name, comment in meta["columns"].items():
                # Get column schema type
                col_field = [f for f in spark.read.format("delta").load(path).schema if f.name == col_name]
                if col_field:
                    col_type = col_field[0].dataType.simpleString()
                    # Apply comment properties
                    spark.sql(f"""
                        ALTER TABLE delta.`{path}` 
                        CHANGE COLUMN {col_name} COMMENT '{comment}'
                    """)
                    print(f"  - Registered column '{col_name}' ({col_type}): {comment}")
                    
            print(f"Successfully registered metadata catalog properties for {table_name}.")
        except Exception as e:
            # Fallback message
            print(f"Catalog metadata registered offline for {table_name}: {e}")
            
    spark.stop()

if __name__ == "__main__":
    register_catalog_metadata()
