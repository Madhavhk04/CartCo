import streamlit as st
import pages_impl

# Setup page config
st.set_page_config(
    page_title="CartCo Commerce Lakehouse",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide streamlit default elements and style layout padding
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        
        /* Remove default streamlit page margins for full-screen feel */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"

# Split screen into Custom React-style Sidebar and Custom Content canvas
col_sidebar, col_content = st.columns([1, 4.3])

with col_sidebar:
    # Sidebar Header
    st.markdown("""
        <div style='padding: 10px 0px 20px 0px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 20px;'>
            <h2 style='color:#ffffff; font-weight:800; font-size:1.5rem; margin:0;'>⚡ CartCo</h2>
            <div style='color:#6366f1; font-size:0.8rem; font-weight:600; margin-top:2px;'>LAKEHOUSE PLATFORM</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Custom CSS style for navigation buttons
    st.markdown("""
        <style>
            /* Target sidebar column buttons to look like native React links */
            div[data-testid="column"]:first-child button {
                text-align: left !important;
                justify-content: flex-start !important;
                border-radius: 10px !important;
                padding: 12px 16px !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                margin-bottom: 8px !important;
                border: none !important;
                transition: all 0.2s ease !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation mapping
    pages = {
        "overview": "📈 Executive Overview",
        "revenue": "💰 Revenue Analytics",
        "customers": "👤 Customer 360",
        "inventory": "📦 Inventory Intelligence",
        "monitoring": "🖥️ Platform Monitoring",
        "quality": "🛡️ Data Quality Center",
        "lineage": "🔗 Lineage Explorer"
    }
    
    for page_key, page_label in pages.items():
        is_active = st.session_state.current_page == page_key
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(page_label, key=f"nav_{page_key}", type=btn_type, use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()

with col_content:
    # Render active page content
    if st.session_state.current_page == "overview":
        pages_impl.render_executive_overview()
    elif st.session_state.current_page == "revenue":
        pages_impl.render_revenue_analytics()
    elif st.session_state.current_page == "customers":
        pages_impl.render_customer_360()
    elif st.session_state.current_page == "inventory":
        pages_impl.render_inventory_intelligence()
    elif st.session_state.current_page == "monitoring":
        pages_impl.render_monitoring()
    elif st.session_state.current_page == "quality":
        pages_impl.render_data_quality()
    elif st.session_state.current_page == "lineage":
        pages_impl.render_lineage_explorer()
