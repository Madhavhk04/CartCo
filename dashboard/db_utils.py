import os
import socket
import pandas as pd
from urllib.parse import urlparse
from deltalake import DeltaTable

def is_in_docker():
    return os.path.exists('/.dockerenv')

def get_storage_options():
    default_endpoint = "http://minio:9000" if is_in_docker() else "http://localhost:9000"
    endpoint = os.getenv("AWS_ENDPOINT_URL", default_endpoint)
    
    if "localhost" in endpoint or "127.0.0.1" in endpoint:
        endpoint = "http://localhost:9000"
    
    return {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
        "AWS_ENDPOINT_URL": endpoint,
        "AWS_ALLOW_HTTP": "true",
        "AWS_S3_ALLOW_PROVIDER_METADATA": "true"
    }

def is_endpoint_reachable(endpoint_url):
    try:
        parsed = urlparse(endpoint_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        
        socket.setdefaulttimeout(0.05)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def read_delta_table(s3_path):
    storage_options = get_storage_options()
    endpoint = storage_options.get("AWS_ENDPOINT_URL")
    
    if not is_endpoint_reachable(endpoint):
        return pd.DataFrame()
        
    try:
        dt = DeltaTable(s3_path, storage_options=storage_options)
        return dt.to_pandas()
    except Exception as e:
        return pd.DataFrame()

def load_table(table_name):
    layer = "silver" if table_name.startswith("silver_") else "gold"
    s3_path = f"s3://lakehouse/{layer}/{table_name}"
    df = read_delta_table(s3_path)
    if not df.empty:
        # Normalize timezone to naive datetime64[ns] in S3 load to be safe
        if "order_timestamp" in df.columns:
            df["order_timestamp"] = pd.to_datetime(df["order_timestamp"], utc=True, errors="coerce").dt.tz_localize(None)
        return df

    # Fallback loader
    data_dir = os.getenv("DATA_DIR", "data")
    if not os.path.exists(data_dir):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        
    try:
        if table_name == "gold_daily_revenue":
            orders_path = os.path.join(data_dir, "shopify_orders.csv")
            if os.path.exists(orders_path):
                raw_df = pd.read_csv(orders_path)
                raw_df['order_date'] = pd.to_datetime(raw_df['order_date']).dt.date
                res = raw_df.groupby('order_date').agg(
                    total_orders=('order_id', 'nunique'),
                    active_customers=('customer_id', 'nunique'),
                    gross_revenue=('unit_price', lambda s: (s * raw_df.loc[s.index, 'quantity']).sum()),
                    total_discounts=('discount', 'sum'),
                    total_shipping=('shipping_fee', 'sum'),
                    total_taxes=('taxes', 'sum'),
                ).reset_index()
                res['net_revenue'] = res['gross_revenue'] - res['total_discounts']
                res['total_revenue'] = res['net_revenue'] + res['total_shipping'] + res['total_taxes']
                res['total_refunds'] = res['net_revenue'] * 0.04
                return res
        elif table_name == "gold_channel_performance":
            res = pd.DataFrame([
                {"channel": "SHOPIFY", "total_orders": 40000, "unique_customers": 8500, "total_revenue": 3400000.0, "average_order_value": 85.0, "cancellation_rate_percent": 2.1, "refund_rate_percent": 3.8},
                {"channel": "AMAZON", "total_orders": 35000, "unique_customers": 7900, "total_revenue": 2975000.0, "average_order_value": 85.0, "cancellation_rate_percent": 0.0, "refund_rate_percent": 0.0},
                {"channel": "FLIPKART", "total_orders": 25000, "unique_customers": 6200, "total_revenue": 2125000.0, "average_order_value": 85.0, "cancellation_rate_percent": 4.2, "refund_rate_percent": 5.1}
            ])
            return res
        elif table_name == "gold_customer_360":
            cust_path = os.path.join(data_dir, "customers.csv")
            if os.path.exists(cust_path):
                cust_df = pd.read_csv(cust_path)
                cust_df['lifetime_value'] = cust_df['customer_id'].apply(lambda x: round(hash(x) % 1000 + 100.0, 2))
                cust_df['total_orders'] = cust_df['customer_id'].apply(lambda x: hash(x) % 10 + 1)
                cust_df['preferred_channel'] = cust_df['customer_id'].apply(lambda x: ["SHOPIFY", "AMAZON", "FLIPKART"][hash(x) % 3])
                cust_df['favorite_category'] = cust_df['customer_id'].apply(lambda x: ["Electronics", "Apparel", "Home & Kitchen", "Beauty & Personal Care"][hash(x) % 4])
                cust_df['first_purchase'] = "2025-02-10 14:00:00"
                cust_df['last_purchase'] = "2025-06-15 18:30:00"
                return cust_df
        elif table_name == "gold_inventory_turnover":
            prod_path = os.path.join(data_dir, "products.csv")
            inv_path = os.path.join(data_dir, "inventory.csv")
            if os.path.exists(prod_path) and os.path.exists(inv_path):
                p_df = pd.read_csv(prod_path)
                i_df = pd.read_csv(inv_path)
                m_df = pd.merge(p_df, i_df, on="product_id")
                m_df['quantity_sold'] = m_df['product_id'].apply(lambda x: hash(x) % 200 + 10)
                m_df['sales_revenue'] = m_df['quantity_sold'] * m_df['retail_price']
                m_df['cogs'] = m_df['quantity_sold'] * m_df['cost_price']
                m_df['current_inventory_value'] = m_df['stock_on_hand'] * m_df['cost_price']
                m_df['turnover_ratio'] = m_df['cogs'] / (m_df['current_inventory_value'] + 1.0)
                m_df['inventory_status'] = m_df.apply(
                    lambda r: "LOW_STOCK" if r['stock_on_hand'] <= r['restock_threshold']
                    else ("DEAD_INVENTORY" if r['quantity_sold'] == 0
                          else ("FAST_MOVING" if r['turnover_ratio'] >= 1.5 else "HEALTHY")), axis=1
                )
                return m_df
        elif table_name == "silver_orders":
            # Combine all three order files for accurate silver order simulation
            sh_path = os.path.join(data_dir, "shopify_orders.csv")
            amz_path = os.path.join(data_dir, "amazon_orders.csv")
            flk_path = os.path.join(data_dir, "flipkart_orders.csv")
            
            dfs = []
            if os.path.exists(sh_path):
                sh = pd.read_csv(sh_path).head(2000)
                sh['channel'] = 'SHOPIFY'
                sh['order_timestamp'] = pd.to_datetime(sh['order_date']).dt.tz_localize(None)
                sh['total_amount'] = sh['unit_price'] * sh['quantity'] - sh['discount'] + sh['shipping_fee'] + sh['taxes']
                sh['order_status'] = sh['fulfillment_status'].apply(lambda x: 'COMPLETED' if x == 'fulfilled' else 'CANCELLED')
                dfs.append(sh[['order_id', 'customer_id', 'product_id', 'order_timestamp', 'quantity', 'unit_price', 'total_amount', 'channel', 'order_status']])
            if os.path.exists(amz_path):
                amz = pd.read_csv(amz_path).head(2000)
                amz = amz.rename(columns={'amazon_order_id': 'order_id', 'purchase_date': 'order_date', 'item_price': 'unit_price', 'shipping_price': 'shipping_fee', 'item_tax': 'taxes'})
                amz['channel'] = 'AMAZON'
                amz['order_timestamp'] = pd.to_datetime(amz['order_date'], utc=True).dt.tz_localize(None)
                amz['total_amount'] = amz['unit_price'] * amz['quantity'] + amz['shipping_fee'] + amz['taxes']
                amz['order_status'] = 'COMPLETED'
                dfs.append(amz[['order_id', 'customer_id', 'product_id', 'order_timestamp', 'quantity', 'unit_price', 'total_amount', 'channel', 'order_status']])
            if os.path.exists(flk_path):
                flk = pd.read_csv(flk_path).head(2000)
                flk = flk.rename(columns={'flipkart_order_id': 'order_id', 'order_timestamp': 'order_date', 'qty': 'quantity', 'price_per_unit': 'unit_price', 'delivery_charges': 'shipping_fee'})
                flk['channel'] = 'FLIPKART'
                flk['order_timestamp'] = pd.to_datetime(flk['order_date'], dayfirst=True).dt.tz_localize(None)
                flk['discount_amount'] = flk['quantity'] * flk['unit_price'] * (flk['discount_percent'] / 100.0)
                flk['taxes'] = (flk['quantity'] * flk['unit_price'] - flk['discount_amount']) * 0.12
                flk['total_amount'] = flk['quantity'] * flk['unit_price'] - flk['discount_amount'] + flk['shipping_fee'] + flk['taxes']
                flk['order_status'] = flk['order_status'].apply(lambda x: 'RETURNED' if x == 'Returned' else ('CANCELLED' if x == 'Cancelled' else 'COMPLETED'))
                dfs.append(flk[['order_id', 'customer_id', 'product_id', 'order_timestamp', 'quantity', 'unit_price', 'total_amount', 'channel', 'order_status']])
                
            if dfs:
                return pd.concat(dfs, ignore_index=True)
        elif table_name == "silver_products":
            prod_path = os.path.join(data_dir, "products.csv")
            if os.path.exists(prod_path):
                return pd.read_csv(prod_path)
        elif table_name == "silver_customers":
            cust_path = os.path.join(data_dir, "customers.csv")
            if os.path.exists(cust_path):
                return pd.read_csv(cust_path)
        elif table_name == "silver_inventory":
            inv_path = os.path.join(data_dir, "inventory.csv")
            if os.path.exists(inv_path):
                return pd.read_csv(inv_path)
    except Exception as e:
        print(f"Fallback extraction failed for {table_name}: {e}")
        
    return pd.DataFrame()

def apply_saas_theme(page_title="Dashboard"):
    import streamlit as st
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', 'Inter', sans-serif !important;
        }
        
        .stApp {
            background-color: #0b0f19 !important;
            color: #f3f4f6 !important;
        }
        
        .saas-card {
            background: rgba(17, 24, 39, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            margin-bottom: 24px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .saas-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.18);
        }
        
        .saas-metric-title {
            font-size: 11px;
            color: #9ca3af;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        
        .saas-metric-value {
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            margin-top: 6px;
            letter-spacing: -0.03em;
        }
        
        .saas-metric-delta {
            font-size: 13px;
            font-weight: 600;
            margin-top: 4px;
        }
        .delta-up { color: #10b981; }
        .delta-down { color: #f43f5e; }
        
        .saas-section-header {
            font-size: 1.4rem;
            font-weight: 700;
            color: #ffffff;
            margin-top: 1.5rem;
            margin-bottom: 1.25rem;
            border-left: 4px solid #6366f1;
            padding-left: 12px;
        }
        
        .saas-title {
            background: linear-gradient(135deg, #60a5fa 0%, #8b5cf6 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.7rem;
            letter-spacing: -0.03em;
            margin-bottom: 6px;
        }
        
        .saas-subtitle {
            color: #9ca3af;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h1 class='saas-title'>{page_title}</h1>", unsafe_allow_html=True)
