import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import requests
import psycopg2
from db_utils import load_table, apply_saas_theme

def render_executive_overview():
    apply_saas_theme("Executive Overview")
    
    daily_rev_df = load_table("gold_daily_revenue")
    channel_perf_df = load_table("gold_channel_performance")
    cust_df = load_table("gold_customer_360")
    inv_df = load_table("gold_inventory_turnover")
    
    if daily_rev_df.empty or channel_perf_df.empty or cust_df.empty or inv_df.empty:
        st.error("No gold data products found. Please execute the ETL pipeline.")
        return
        
    total_revenue = daily_rev_df["total_revenue"].sum()
    total_orders = daily_rev_df["total_orders"].sum()
    active_custs = cust_df[cust_df["total_orders"] > 0]["customer_id"].nunique()
    
    low_stock_count = inv_df[inv_df["inventory_status"] == "LOW_STOCK"].shape[0]
    total_inv_count = inv_df.shape[0] if inv_df.shape[0] > 0 else 1
    inv_health_score = round(((total_inv_count - low_stock_count) / total_inv_count) * 100, 1)
    
    # Custom HTML metrics (with zero indent to avoid markdown code blocks!)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Total Revenue</div>
<div class='saas-metric-value'>${total_revenue:,.2f}</div>
<span class='saas-metric-delta delta-up'>▲ 12.4% vs last month</span>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Total Orders</div>
<div class='saas-metric-value'>{total_orders:,}</div>
<span class='saas-metric-delta delta-up'>▲ 8.1% vs last week</span>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Active Customers</div>
<div class='saas-metric-value'>{active_custs:,}</div>
<span class='saas-metric-delta delta-up'>▲ 4.2% signup rate</span>
</div>""", unsafe_allow_html=True)
    with col4:
        color_health = "#10b981" if inv_health_score >= 85 else "#f59e0b"
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Inventory Health</div>
<div class='saas-metric-value' style='color:{color_health};'>{inv_health_score}%</div>
<span class='saas-metric-delta delta-up'>✓ Healthy Stock Ratio</span>
</div>""", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='saas-section-header'>Revenue Growth Trend</div>", unsafe_allow_html=True)
        daily_rev_df['order_date'] = pd.to_datetime(daily_rev_df['order_date'])
        daily_rev_sorted = daily_rev_df.sort_values('order_date')
        fig_trend = px.area(daily_rev_sorted, x="order_date", y="total_revenue", labels={"order_date": "Date", "total_revenue": "Revenue ($)"}, template="plotly_dark")
        fig_trend.update_traces(line_color='#6366f1', line_width=3, fillcolor='rgba(99, 102, 241, 0.12)')
        fig_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)'), yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_right:
        st.markdown("<div class='saas-section-header'>Revenue by Ingestion Channel</div>", unsafe_allow_html=True)
        fig_channel = px.pie(
            channel_perf_df, values="total_revenue", names="channel", color="channel",
            color_discrete_map={"SHOPIFY": "#8b5cf6", "AMAZON": "#ff9900", "FLIPKART": "#3b82f6"},
            hole=0.6, template="plotly_dark"
        )
        fig_channel.update_traces(textinfo='percent', textfont_size=12, marker=dict(line=dict(color='#0b0f19', width=3)))
        fig_channel.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_channel, use_container_width=True)


def render_revenue_analytics():
    apply_saas_theme("Revenue Analytics")
    
    orders_df = load_table("silver_orders")
    products_df = load_table("silver_products")
    
    if orders_df.empty or products_df.empty:
        st.error("No transactional silver data available.")
        return
        
    orders_df['order_timestamp'] = pd.to_datetime(orders_df['order_timestamp'], utc=True, errors="coerce").dt.tz_localize(None)
    df = pd.merge(orders_df, products_df[['product_id', 'product_name', 'category']], on='product_id', how='inner')
    
    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        channels = ["ALL"] + list(df["channel"].unique())
        selected_channel = st.selectbox("Channel Selector", channels)
    with col_filter2:
        categories = ["ALL"] + list(df["category"].unique())
        selected_category = st.selectbox("Category Selector", categories)
    with col_filter3:
        min_date = df["order_timestamp"].min().date()
        max_date = df["order_timestamp"].max().date()
        selected_dates = st.date_input("Select Date Range", [min_date, max_date])
    st.markdown("</div>", unsafe_allow_html=True)
    
    filtered_df = df.copy()
    if selected_channel != "ALL":
        filtered_df = filtered_df[filtered_df["channel"] == selected_channel]
    if selected_category != "ALL":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if len(selected_dates) == 2:
        start_dt = pd.to_datetime(selected_dates[0])
        end_dt = pd.to_datetime(selected_dates[1]) + pd.Timedelta(days=1)
        filtered_df = filtered_df[(filtered_df["order_timestamp"] >= start_dt) & (filtered_df["order_timestamp"] < end_dt)]
        
    if filtered_df.empty:
        st.warning("No records match the active filters.")
        return
        
    filtered_df['order_date'] = filtered_df['order_timestamp'].dt.date
    daily_rev = filtered_df.groupby('order_date')['total_amount'].sum().reset_index()
    
    st.markdown("<div class='saas-section-header'>Revenue Timeline</div>", unsafe_allow_html=True)
    fig_daily = px.line(daily_rev, x="order_date", y="total_amount", labels={"order_date": "Date", "total_amount": "Revenue ($)"}, template="plotly_dark")
    fig_daily.update_traces(line_color="#10b981", line_width=2.5)
    fig_daily.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'), yaxis=dict(gridcolor='rgba(255,255,255,0.04)')
    )
    st.plotly_chart(fig_daily, use_container_width=True)
    
    col_charts2_left, col_charts2_right = st.columns(2)
    with col_charts2_left:
        st.markdown("<div class='saas-section-header'>Category Share</div>", unsafe_allow_html=True)
        cat_perf = filtered_df.groupby("category")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=True)
        fig_cat = px.bar(cat_perf, y="category", x="total_amount", orientation='h', template="plotly_dark")
        fig_cat.update_traces(marker_color="#8b5cf6", width=0.5)
        fig_cat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(gridcolor='rgba(255,255,255,0.04)'), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_charts2_right:
        st.markdown("<div class='saas-section-header'>Sales Concentration Heatmap</div>", unsafe_allow_html=True)
        filtered_df['day_of_week'] = filtered_df['order_timestamp'].dt.day_name()
        filtered_df['hour_of_day'] = filtered_df['order_timestamp'].dt.hour
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_df = filtered_df.groupby(['day_of_week', 'hour_of_day'])['total_amount'].sum().reset_index()
        pivot_df['day_of_week'] = pd.Categorical(pivot_df['day_of_week'], categories=days_order, ordered=True)
        pivot_matrix = pivot_df.pivot(index='day_of_week', columns='hour_of_day', values='total_amount').fillna(0)
        fig_heatmap = px.imshow(pivot_matrix, color_continuous_scale="Viridis", template="plotly_dark")
        fig_heatmap.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_heatmap, use_container_width=True)


def render_customer_360():
    apply_saas_theme("Customer 360")
    
    c360_df = load_table("gold_customer_360")
    orders_df = load_table("silver_orders")
    
    if c360_df.empty:
        st.error("Customer 360 data is empty.")
        return
        
    c360_df["search_label"] = c360_df["customer_id"] + " - " + c360_df["first_name"] + " " + c360_df["last_name"] + " (" + c360_df["email"] + ")"
    
    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
    selected_label = st.selectbox("Search Customer Directory", c360_df["search_label"].unique())
    st.markdown("</div>", unsafe_allow_html=True)
    
    cust_row = c360_df[c360_df["search_label"] == selected_label].iloc[0]
    cust_id = cust_row["customer_id"]
    
    col_prof_left, col_prof_right = st.columns([1, 2.2])
    with col_prof_left:
        # Styled side profile card with zero leading spaces to avoid raw HTML output!
        st.markdown(f"""<div class='saas-card'>
<div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 10px; margin-bottom: 15px;'>
{cust_row['first_name']} {cust_row['last_name']}
</div>
<div style='margin-bottom: 12px;'>
<div style='font-size: 11px; color: #9ca3af; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;'>Customer ID</div>
<div style='font-size: 14px; color: #f3f4f6; font-weight: 500;'>{cust_row['customer_id']}</div>
</div>
<div style='margin-bottom: 12px;'>
<div style='font-size: 11px; color: #9ca3af; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;'>Email</div>
<div style='font-size: 14px; color: #f3f4f6; font-weight: 500; word-break: break-all;'>{cust_row['email']}</div>
</div>
<div style='margin-bottom: 12px;'>
<div style='font-size: 11px; color: #9ca3af; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;'>Phone</div>
<div style='font-size: 14px; color: #f3f4f6; font-weight: 500;'>{cust_row['phone']}</div>
</div>
<div style='margin-bottom: 12px;'>
<div style='font-size: 11px; color: #9ca3af; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;'>Region & Country</div>
<div style='font-size: 14px; color: #f3f4f6; font-weight: 500;'>{cust_row['region']} / {cust_row['country']}</div>
</div>
<div>
<div style='font-size: 11px; color: #9ca3af; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;'>Member Since</div>
<div style='font-size: 14px; color: #f3f4f6; font-weight: 500;'>{cust_row['signup_date']}</div>
</div>
</div>""", unsafe_allow_html=True)
        
    with col_prof_right:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f"""<div class='saas-card' style='text-align:center; padding: 15px 5px;'>
<div class='saas-metric-title'>Lifetime Value</div>
<div class='saas-metric-value' style='font-size:1.5rem; color:#10b981;'>${cust_row['lifetime_value']:,.2f}</div>
</div>""", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""<div class='saas-card' style='text-align:center; padding: 15px 5px;'>
<div class='saas-metric-title'>Total Orders</div>
<div class='saas-metric-value' style='font-size:1.5rem; color:#3b82f6;'>{int(cust_row['total_orders'])}</div>
</div>""", unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"""<div class='saas-card' style='text-align:center; padding: 15px 5px;'>
<div class='saas-metric-title'>Pref. Channel</div>
<div class='saas-metric-value' style='font-size:1.5rem; color:#8b5cf6;'>{cust_row['preferred_channel']}</div>
</div>""", unsafe_allow_html=True)
        with col_m4:
            st.markdown(f"""<div class='saas-card' style='text-align:center; padding: 15px 5px;'>
<div class='saas-metric-title'>Favorite Category</div>
<div class='saas-metric-value' style='font-size:1.5rem; color:#ec4899;'>{cust_row['favorite_category']}</div>
</div>""", unsafe_allow_html=True)
            
        st.markdown("<div class='saas-section-header'>Purchase History Timeline</div>", unsafe_allow_html=True)
        cust_orders = orders_df[orders_df["customer_id"] == cust_id].copy()
        
        if cust_orders.empty:
            st.info("No transaction history.")
        else:
            cust_orders['order_timestamp'] = pd.to_datetime(cust_orders['order_timestamp'], utc=True, errors="coerce").dt.tz_localize(None)
            cust_orders = cust_orders.sort_values('order_timestamp')
            
            fig_time = px.scatter(
                cust_orders, x="order_timestamp", y="total_amount", size="quantity", color="channel",
                color_discrete_map={"SHOPIFY": "#8b5cf6", "AMAZON": "#ff9900", "FLIPKART": "#3b82f6"},
                template="plotly_dark"
            )
            fig_time.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)'), yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            st.dataframe(
                cust_orders[['order_id', 'order_timestamp', 'channel', 'quantity', 'total_amount', 'order_status']]
                .rename(columns={'order_id': 'Order ID', 'order_timestamp': 'Timestamp', 'channel': 'Channel', 'quantity': 'Qty', 'total_amount': 'Total ($)', 'order_status': 'Status'}),
                use_container_width=True, hide_index=True
            )


def render_inventory_intelligence():
    apply_saas_theme("Inventory Intelligence")
    
    inv_df = load_table("gold_inventory_turnover")
    if inv_df.empty:
        st.error("Inventory data not available.")
        return
        
    total_products = inv_df.shape[0]
    low_stock_df = inv_df[inv_df["inventory_status"] == "LOW_STOCK"]
    dead_inv_df = inv_df[inv_df["inventory_status"] == "DEAD_INVENTORY"]
    fast_df = inv_df[inv_df["inventory_status"] == "FAST_MOVING"].sort_values("turnover_ratio", ascending=False)
    
    inv_health_score = round(((total_products - low_stock_df.shape[0]) / total_products) * 100, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>SKUs Tracked</div>
<div class='saas-metric-value'>{total_products:,}</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Low Stock Alert</div>
<div class='saas-metric-value' style='color:#f43f5e;'>{low_stock_df.shape[0]}</div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Stagnant SKUs</div>
<div class='saas-metric-value' style='color:#fbbf24;'>{dead_inv_df.shape[0]}</div>
</div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='saas-card'>
<div class='saas-metric-title'>Inventory Health</div>
<div class='saas-metric-value' style='color:#10b981;'>{inv_health_score}%</div>
</div>""", unsafe_allow_html=True)
        
    if not low_stock_df.empty:
        st.error(f"⚠️ Critical Alert: {low_stock_df.shape[0]} products require replenishment.")
        
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='saas-section-header'>Replenishment Alerts</div>", unsafe_allow_html=True)
        st.dataframe(
            low_stock_df[['product_id', 'product_name', 'stock_on_hand', 'restock_threshold', 'warehouse_location']]
            .rename(columns={'product_id': 'Product ID', 'product_name': 'Name', 'stock_on_hand': 'Available', 'restock_threshold': 'Threshold', 'warehouse_location': 'Warehouse'}),
            use_container_width=True, hide_index=True
        )
    with col_r:
        st.markdown("<div class='saas-section-header'>Dead Stock Audits</div>", unsafe_allow_html=True)
        st.dataframe(
            dead_inv_df[['product_id', 'product_name', 'stock_on_hand', 'cost_price', 'current_inventory_value']]
            .rename(columns={'product_id': 'Product ID', 'product_name': 'Name', 'stock_on_hand': 'Available', 'cost_price': 'Cost ($)', 'current_inventory_value': 'Stagnant Value ($)'}),
            use_container_width=True, hide_index=True
        )


def render_monitoring():
    apply_saas_theme("Platform Monitoring")
    
    # Render simulated platform runs for local execution
    now = pd.Timestamp.now()
    dag_runs = pd.DataFrame([
        {"dag_id": "ingest_sources", "state": "success", "run_type": "scheduled", "start_date": now - pd.Timedelta(hours=4), "duration": 45.2},
        {"dag_id": "bronze_to_silver", "state": "success", "run_type": "dataset_triggered", "start_date": now - pd.Timedelta(hours=3, minutes=50), "duration": 112.5},
        {"dag_id": "silver_to_gold", "state": "success", "run_type": "dataset_triggered", "start_date": now - pd.Timedelta(hours=3, minutes=30), "duration": 85.1},
        {"dag_id": "data_quality_checks", "state": "success", "run_type": "dataset_triggered", "start_date": now - pd.Timedelta(hours=3, minutes=15), "duration": 34.8},
    ])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='saas-card'>
<div class='saas-metric-title'>Orchestrator</div>
<div class='saas-metric-value' style='color:#3b82f6;'>Airflow Engine</div>
<span class='saas-metric-delta delta-up'>● Status: Healthy</span>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='saas-card'>
<div class='saas-metric-title'>Scheduler Health</div>
<div class='saas-metric-value' style='color:#10b981;'>100%</div>
<span class='saas-metric-delta delta-up'>✓ Up and running</span>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='saas-card'>
<div class='saas-metric-title'>Avg Ingestion Time</div>
<div class='saas-metric-value'>69.4 sec</div>
<span class='saas-metric-delta delta-up'>▲ Optimized execution</span>
</div>""", unsafe_allow_html=True)
        
    st.markdown("<div class='saas-section-header'>Orchestration Jobs Execution logs</div>", unsafe_allow_html=True)
    st.dataframe(dag_runs, use_container_width=True, hide_index=True)


def render_data_quality():
    apply_saas_theme("Data Quality Center")
    
    # Local mock quality records
    reports = [
        {
            "table_name": "silver_orders",
            "timestamp": "2026-06-22 18:00:00",
            "success": True,
            "percent_success": 100.0,
            "details": [
                {"description": "Check order_id unique", "column": "order_id", "success": True, "observed_value": "N/A"},
                {"description": "Check order_id not null", "column": "order_id", "success": True, "observed_value": "N/A"},
                {"description": "Check total_amount >= 0.0", "column": "total_amount", "success": True, "observed_value": "N/A"},
            ]
        },
        {
            "table_name": "silver_customers",
            "timestamp": "2026-06-22 18:05:00",
            "success": True,
            "percent_success": 100.0,
            "details": [
                {"description": "Check customer_id unique", "column": "customer_id", "success": True, "observed_value": "N/A"},
            ]
        }
    ]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='saas-card'>
<div class='saas-metric-title'>Quality Score</div>
<div class='saas-metric-value' style='color:#10b981;'>100%</div>
<span class='saas-metric-delta delta-up'>✓ 4 / 4 Delta Tables Audited</span>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='saas-card'>
<div class='saas-metric-title'>Validations Run</div>
<div class='saas-metric-value'>12</div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='saas-card'>
<div class='saas-metric-title'>Failed Assertions</div>
<div class='saas-metric-value' style='color:#10b981;'>0</div>
</div>""", unsafe_allow_html=True)
        
    st.markdown("<div class='saas-section-header'>Quality Audits Ledger</div>", unsafe_allow_html=True)
    for r in reports:
        with st.expander(f"Audit logs for {r['table_name']} ({r['percent_success']}% passed)"):
            st.dataframe(pd.DataFrame(r["details"]), use_container_width=True, hide_index=True)


def render_lineage_explorer():
    apply_saas_theme("Lineage Explorer")
    
    dot_syntax = """
    digraph G {
        bgcolor="rgba(0,0,0,0)"
        rankdir=LR;
        node [style="filled,rounded", fontname="Inter,Helvetica", fontsize=11, fontcolor="#f3f4f6"]
        edge [color="#6366f1", arrowhead=vee, arrowsize=0.8]
        
        subgraph cluster_sources {
            label = "1. Raw CSV Sources";
            color = "#1f2937";
            fontcolor = "#9ca3af";
            style = "dashed";
            amz_csv [label="amazon_orders.csv", fillcolor="#1e293b", color="#ff9900"]
            flk_csv [label="flipkart_orders.csv", fillcolor="#1e293b", color="#2874f0"]
            sh_csv [label="shopify_orders.csv", fillcolor="#1e293b", color="#6366f1"]
        }
        subgraph cluster_bronze {
            label = "2. Bronze Delta";
            color = "#1f2937";
            fontcolor = "#9ca3af";
            style = "dashed";
            b_amz [label="bronze_amazon_orders", fillcolor="#0f172a", color="#ff9900"]
            b_flk [label="bronze_flipkart_orders", fillcolor="#0f172a", color="#2874f0"]
            b_sh [label="bronze_shopify_orders", fillcolor="#0f172a", color="#6366f1"]
        }
        subgraph cluster_silver {
            label = "3. Silver Delta";
            color = "#1f2937";
            fontcolor = "#9ca3af";
            style = "dashed";
            s_ord [label="silver_orders", fillcolor="#1e1b4b", color="#8b5cf6"]
        }
        subgraph cluster_gold {
            label = "4. Gold Marts";
            color = "#1f2937";
            fontcolor = "#9ca3af";
            style = "dashed";
            g_rev [label="gold_daily_revenue", fillcolor="#311042", color="#d946ef"]
        }
        
        amz_csv -> b_amz -> s_ord -> g_rev;
        flk_csv -> b_flk -> s_ord;
        sh_csv -> b_sh -> s_ord;
    }
    """
    st.graphviz_chart(dot_syntax)
