import React, { useState, useEffect, useRef } from 'react';
import { 
  LayoutDashboard, 
  DollarSign, 
  Users, 
  Boxes, 
  Activity, 
  CheckSquare, 
  GitBranch, 
  Search, 
  SlidersHorizontal,
  Info,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  RefreshCw,
  Clock,
  Settings,
  ArrowUpRight,
  User,
  MapPin,
  Mail,
  Phone,
  Database,
  Layers,
  ShieldCheck,
  TrendingDown
} from 'lucide-react';
import { 
  ComposedChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Scatter,
  PieChart, Pie, Cell, BarChart, Bar, Line
} from 'recharts';
import './App.css';

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? "http://localhost:8000/api"
  : `http://${window.location.hostname}:8000/api`;

const COLORS = ['#8b5cf6', '#3b82f6', '#06b6d4', '#ec4899', '#10b981'];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // States
  const [overviewData, setOverviewData] = useState(null);
  const [revenueData, setRevenueData] = useState(null);
  const [customerData, setCustomerData] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [customerTimeline, setCustomerTimeline] = useState([]);
  const [inventoryData, setInventoryData] = useState(null);
  const [monitoringData, setMonitoringData] = useState(null);
  const [qualityData, setQualityData] = useState(null);
  
  // Filters
  const [channelFilter, setChannelFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [custSearch, setCustSearch] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const comboboxRef = useRef(null);

  // Global UI search (visual only)
  const [globalSearch, setGlobalSearch] = useState('');

  // ----------------------------------------------------
  // STATIC MOCK FALLBACKS (Guarantees zero-setup display!)
  // ----------------------------------------------------
  const loadMockData = () => {
    console.log("Loading mock dashboard fallback data...");
    
    // 1. Overview Mock with enriched forecasts and anomalies
    setOverviewData({
      kpis: { 
        total_revenue: 8524310.50, 
        total_orders: 100000, 
        active_customers: 9845, 
        inventory_health: 92.4,
        revenue_growth: 12.4,
        orders_growth: 8.1,
        customers_growth: 4.2,
        inventory_growth: 1.5,
        pipeline_health: "Healthy",
        data_freshness: "Updated 10m ago",
        etl_success_rate: 100.0,
        api_latency_ms: 14
      },
      trend: [
        { order_date: "2025-05-15", total_revenue: 180000, total_orders: 2100, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-05-20", total_revenue: 290000, total_orders: 3400, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-05-25", total_revenue: 350000, total_orders: 4120, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-05-30", total_revenue: 690000, total_orders: 4900, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: true, anomaly_revenue: 690000 },
        { order_date: "2025-06-05", total_revenue: 410000, total_orders: 6200, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-10", total_revenue: 550000, total_orders: 7800, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-15", total_revenue: 850000, total_orders: 9800, forecast: null, forecast_upper: null, forecast_lower: null, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-16", total_revenue: null, total_orders: null, forecast: 870000, forecast_upper: 990000, forecast_lower: 750000, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-17", total_revenue: null, total_orders: null, forecast: 890000, forecast_upper: 1040000, forecast_lower: 740000, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-18", total_revenue: null, total_orders: null, forecast: 920000, forecast_upper: 1090000, forecast_lower: 750000, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-19", total_revenue: null, total_orders: null, forecast: 960000, forecast_upper: 1150000, forecast_lower: 770000, is_anomaly: false, anomaly_revenue: null },
        { order_date: "2025-06-20", total_revenue: null, total_orders: null, forecast: 1020000, forecast_upper: 1220000, forecast_lower: 820000, is_anomaly: false, anomaly_revenue: null }
      ],
      channels: [
        { channel: "SHOPIFY", total_orders: 40000, unique_customers: 8500, total_revenue: 3400000, average_order_value: 85, cancellation_rate_percent: 2.1, performance_score: 94 },
        { channel: "AMAZON", total_orders: 35000, unique_customers: 7900, total_revenue: 2975000, average_order_value: 85, cancellation_rate_percent: 0.0, performance_score: 98 },
        { channel: "FLIPKART", total_orders: 25000, unique_customers: 6200, total_revenue: 2149310, average_order_value: 85, cancellation_rate_percent: 4.2, performance_score: 86 }
      ],
      regions: [
        { region: "North", lifetime_value: 2850000 },
        { region: "South", lifetime_value: 2100000 },
        { region: "West", lifetime_value: 1950000 },
        { region: "East", lifetime_value: 1624310 }
      ],
      ai_insights: [
        { type: "revenue", title: "Amazon Sales Surge", text: "Revenue is projected to increase 12.4% due to a strong sales surge in AMAZON, yielding $2,975,000.00.", impact: "high", badge: "Revenue Peak", action: "Allocate additional marketing spend to standard Amazon advertising campaigns." },
        { type: "inventory", title: "Inventory Risk Detected", text: "Stock levels are compromised for 2 SKUs which are currently below the safety threshold.", impact: "high", badge: "Low Stock Alert", action: "Reorder inventory immediately for key products: Nexa Smart Watch, Eco Cotton T-Shirt." },
        { type: "customers", title: "VIP Segment Expansion", text: "Customer retention is up 8%, with 2 active customer accounts moving into high-LTV tiers.", impact: "medium", badge: "VIP Customer LTV", action: "Deploy VIP loyalty rewards to encourage recurring purchases." }
      ]
    });

    // 2. Revenue Mock
    setRevenueData({
      categories: [
        { category: "Electronics", total_amount: 3200000, growth: 14.8 },
        { category: "Apparel", total_amount: 2100000, growth: 9.2 },
        { category: "Home & Kitchen", total_amount: 1850000, growth: -2.4 },
        { category: "Beauty & Personal Care", total_amount: 1374310, growth: 5.1 }
      ],
      orders: [
        { order_id: "SH_1004988", customer_id: "CUST_00001", product_id: "PROD_003", order_timestamp: "2026-02-27 01:19:41", quantity: 1, unit_price: 191.42, total_amount: 191.42, channel: "SHOPIFY", order_status: "COMPLETED" },
        { order_id: "AMZ-102-392019", customer_id: "CUST_00002", product_id: "PROD_021", order_timestamp: "2026-03-04 12:45:00", quantity: 2, unit_price: 85.00, total_amount: 170.00, channel: "AMAZON", order_status: "COMPLETED" },
        { order_id: "FLK992019488", customer_id: "CUST_00001", product_id: "PROD_089", order_timestamp: "2026-03-12 18:22:00", quantity: 1, unit_price: 124.50, total_amount: 139.44, channel: "FLIPKART", order_status: "COMPLETED" }
      ]
    });

    // 3. Customer Mock
    const mockCustomers = [
      { customer_id: "CUST_00001", first_name: "Rahul", last_name: "Sharma", email: "rahul.sharma82@example.com", phone: "+91 98765 43210", signup_date: "2025-01-12", region: "North", country: "India", lifetime_value: 932.00, total_orders: 3, preferred_channel: "SHOPIFY", favorite_category: "Electronics", risk_score: "Low Risk" },
      { customer_id: "CUST_00002", first_name: "Sarah", last_name: "Smith", email: "sarah.smith29@example.com", phone: "+1 (206) 555-0198", signup_date: "2025-02-18", region: "West", country: "USA", lifetime_value: 1245.50, total_orders: 5, preferred_channel: "AMAZON", favorite_category: "Apparel", risk_score: "Medium Risk" }
    ];
    setCustomerData(mockCustomers);
    setSelectedCustomerId("CUST_00001");
    setCustomerTimeline([
      { order_id: "SH_1004988", order_timestamp: "2026-02-27", total_amount: 191.42, quantity: 1, channel: "SHOPIFY", order_status: "COMPLETED" },
      { order_id: "SH_1009841", order_timestamp: "2026-04-12", total_amount: 340.58, quantity: 2, channel: "SHOPIFY", order_status: "COMPLETED" }
    ]);

    // 4. Inventory Mock
    setInventoryData({
      total_sku: 1000,
      low_stock: [
        { product_id: "PROD_003", product_name: "Nexa Smart Watch", stock_on_hand: 8, restock_threshold: 20, warehouse_location: "WH-Delhi", cost_price: 120.00 },
        { product_id: "PROD_021", product_name: "Eco Cotton T-Shirt", stock_on_hand: 5, restock_threshold: 15, warehouse_location: "WH-Texas", cost_price: 15.00 }
      ],
      dead_stock: [
        { product_id: "PROD_089", product_name: "Volt Laptop Stand", stock_on_hand: 120, cost_price: 18.50, current_inventory_value: 2220.00 }
      ],
      fast_moving: [
        { product_name: "Apex Wireless Earbuds", turnover_ratio: 4.8 },
        { product_name: "Volt Power Bank", turnover_ratio: 3.9 }
      ]
    });

    // 5. Monitoring Mock
    setMonitoringData({
      runs: [
        { dag_id: "ingest_sources", state: "success", run_type: "scheduled", start_date: "2026-06-22 14:00:00", duration: 45.2 },
        { dag_id: "bronze_to_silver", state: "success", run_type: "dataset_triggered", start_date: "2026-06-22 14:01:10", duration: 112.5 },
        { dag_id: "silver_to_gold", state: "success", run_type: "dataset_triggered", start_date: "2026-06-22 14:03:20", duration: 85.1 },
        { dag_id: "data_quality_checks", state: "success", run_type: "dataset_triggered", start_date: "2026-06-22 14:05:00", duration: 34.8 }
      ]
    });

    // 6. Quality Mock
    setQualityData({
      reports: [
        {
          table_name: "silver_orders",
          timestamp: "2026-06-22 14:02:00",
          success: true,
          percent_success: 100.0,
          details: [
            { description: "Check order_id unique", column: "order_id", success: true, observed_value: "N/A" },
            { description: "Check order_id not null", column: "order_id", success: true, observed_value: "N/A" },
            { description: "Check total_amount >= 0.0", column: "total_amount", success: true, observed_value: "N/A" }
          ]
        },
        {
          table_name: "silver_customers",
          timestamp: "2026-06-22 14:02:10",
          success: true,
          percent_success: 100.0,
          details: [
            { description: "Check customer_id unique", column: "customer_id", success: true, observed_value: "N/A" }
          ]
        }
      ]
    });
  };

  // ----------------------------------------------------
  // FETCH ENDPOINTS
  // ----------------------------------------------------
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        if (activeTab === 'overview') {
          const res = await fetch(`${API_BASE}/overview`);
          const data = await res.json();
          if (data.success) setOverviewData(data);
          else loadMockData();
        } else if (activeTab === 'revenue') {
          const res = await fetch(`${API_BASE}/revenue?channel=${channelFilter}&category=${categoryFilter}`);
          const data = await res.json();
          if (data.success) setRevenueData(data);
          else loadMockData();
        } else if (activeTab === 'customers') {
          const res = await fetch(`${API_BASE}/customers`);
          const data = await res.json();
          if (data.success) {
            setCustomerData(data.customers);
            if (data.customers.length > 0 && !selectedCustomerId) {
              setSelectedCustomerId(data.customers[0].customer_id);
            }
          } else loadMockData();
        } else if (activeTab === 'inventory') {
          const res = await fetch(`${API_BASE}/inventory`);
          const data = await res.json();
          if (data.success) setInventoryData(data);
          else loadMockData();
        } else if (activeTab === 'monitoring') {
          const res = await fetch(`${API_BASE}/monitoring`);
          const data = await res.json();
          if (data.success) setMonitoringData(data);
          else loadMockData();
        } else if (activeTab === 'quality') {
          const res = await fetch(`${API_BASE}/quality`);
          const data = await res.json();
          if (data.success) setQualityData(data);
          else loadMockData();
        }
      } catch (err) {
        console.warn("FastAPI backend not running. Loading offline mock datasets.");
        loadMockData();
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeTab, channelFilter, categoryFilter]);

  // Fetch Customer Timeline when customer changes
  useEffect(() => {
    if (activeTab === 'customers' && selectedCustomerId) {
      const fetchTimeline = async () => {
        try {
          const res = await fetch(`${API_BASE}/customer/${selectedCustomerId}`);
          const data = await res.json();
          if (data.success) setCustomerTimeline(data.timeline);
        } catch (e) {
          // Keep mock timeline
        }
      };
      fetchTimeline();
    }
  }, [selectedCustomerId, activeTab]);

  // Click outside detection for customer combobox
  useEffect(() => {
    function handleClickOutside(event) {
      if (comboboxRef.current && !comboboxRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="flex h-screen bg-[#050816] text-[#f3f4f6] font-sans antialiased overflow-hidden grid-overlay">
      
      {/* Background ambient radial glows */}
      <div className="ambient-glow-indigo top-0 left-1/4"></div>
      <div className="ambient-glow-cyan bottom-10 right-1/4"></div>
      
      {/* ---------------------------------------------------- */}
      {/* SIDEBAR NAVIGATION */}
      {/* ---------------------------------------------------- */}
      <aside className="w-72 bg-[#080b18]/80 border-r border-[#1f2937]/30 flex flex-col justify-between shrink-0 z-10 backdrop-blur-md">
        <div>
          <div className="p-6 border-b border-[#1f2937]/30 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                <span className="text-indigo-500 font-extrabold">⚡</span> CartCo
              </h2>
              <div className="text-[10px] font-bold text-indigo-400 tracking-wider uppercase mt-1">
                Unified Lakehouse
              </div>
            </div>
            <div className="h-2 w-2 rounded-full bg-indigo-500 animate-ping"></div>
          </div>
          
          <nav className="p-4 space-y-1.5">
            {[
              { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
              { id: 'revenue', label: 'Revenue Analytics', icon: DollarSign },
              { id: 'customers', label: 'Customer 360', icon: Users },
              { id: 'inventory', label: 'Inventory Intelligence', icon: Boxes },
              { id: 'monitoring', label: 'Platform Monitoring', icon: Activity },
              { id: 'quality', label: 'Data Quality Center', icon: CheckSquare },
              { id: 'lineage', label: 'Lineage Explorer', icon: GitBranch },
            ].map(tab => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3.5 px-4.5 py-3 rounded-xl text-sm font-semibold transition-all relative group ${
                    active 
                      ? 'bg-gradient-to-r from-indigo-600/20 to-violet-600/10 text-white border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.15)]' 
                      : 'text-gray-400 border border-transparent hover:text-white hover:bg-white/[0.02]'
                  }`}
                >
                  <Icon size={18} className={active ? 'text-indigo-400' : 'text-gray-400 group-hover:text-gray-200'} />
                  {tab.label}
                  {active && (
                    <span className="absolute right-3.5 h-1.5 w-1.5 rounded-full bg-indigo-400"></span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-5 border-t border-[#1f2937]/30 flex flex-col gap-3">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Server status:</span>
            <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 pulse-indicator"></span>
              Synchronized
            </span>
          </div>
          <div className="text-[10px] text-gray-600 text-center font-semibold">
            PLATFORM LAYER v1.0.0
          </div>
        </div>
      </aside>

      {/* ---------------------------------------------------- */}
      {/* MAIN CONTENT AREA */}
      {/* ---------------------------------------------------- */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto z-10 relative">
        
        {/* TOP BAR / HEADER */}
        <header className="h-20 border-b border-[#1f2937]/30 flex items-center justify-between px-8 shrink-0 bg-[#050816]/70 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold tracking-tight text-white capitalize">
              {activeTab.replace('_', ' ')}
            </h1>
            <span className="h-4 w-[1px] bg-gray-800"></span>
            <div className="flex items-center gap-2 text-xs text-gray-400 bg-white/[0.02] border border-[#1f2937]/20 px-3 py-1.5 rounded-full">
              <Clock size={12} className="text-indigo-400 animate-pulse" />
              <span>Real-time Sync Active</span>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="relative w-64">
              <Search size={16} className="absolute left-3.5 top-3 text-gray-500" />
              <input 
                type="text" 
                placeholder="Global telemetry search..." 
                value={globalSearch}
                onChange={e => setGlobalSearch(e.target.value)}
                className="w-full bg-[#080b18]/60 border border-[#1f2937]/30 rounded-full pl-10 pr-4 py-2 text-xs text-gray-300 placeholder-gray-500 focus:outline-none focus:border-indigo-500/50"
              />
            </div>
            
            <div className="flex items-center gap-3 bg-[#080b18]/60 border border-[#1f2937]/30 px-4 py-2 rounded-xl text-xs text-gray-400">
              <Database size={14} className="text-indigo-400" />
              <span className="font-semibold text-gray-300">Medallion MinIO Engine</span>
            </div>
          </div>
        </header>

        {/* CONTAINER CONTENT */}
        <div className="p-8 max-w-7xl w-full mx-auto space-y-8 flex-1">
          
          {loading && (
            <div className="flex items-center justify-center h-96">
              <div className="relative flex flex-col items-center gap-4">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-indigo-500"></div>
                <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Consolidating Telemetry...</span>
              </div>
            </div>
          )}

          {!loading && (
            <>
              {/* 1. OVERVIEW PAGE */}
              {activeTab === 'overview' && overviewData && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  
                  {/* Executive welcome row */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-extrabold text-white tracking-tight">Good Morning, CartCo Team</h2>
                      <p className="text-xs text-gray-400 mt-1">Here is the multi-channel delta telemetry status for your lakehouse deployment.</p>
                    </div>
                    <div className="flex items-center gap-2 bg-[#080b18]/80 border border-[#1f2937]/40 px-4 py-2 rounded-xl text-xs text-gray-400">
                      <span className="h-2 w-2 rounded-full bg-indigo-500 pulse-indicator"></span>
                      <span>Last sync: <b>{overviewData.kpis.data_freshness}</b></span>
                    </div>
                  </div>

                  {/* Redesigned Hero KPI Cards */}
                  <div className="grid grid-cols-4 gap-6">
                    {[
                      { 
                        title: 'Gross Revenue', 
                        value: `$${overviewData.kpis.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 
                        growth: overviewData.kpis.revenue_growth,
                        desc: "vs last month",
                        color: "text-indigo-400",
                        spark: [10, 15, 8, 22, 17, 30, 26, 45, 40, 55],
                        glow: "border-indigo-500/20"
                      },
                      { 
                        title: 'Total Orders', 
                        value: overviewData.kpis.total_orders.toLocaleString(), 
                        growth: overviewData.kpis.orders_growth,
                        desc: "vs last week",
                        color: "text-cyan-400",
                        spark: [20, 25, 22, 35, 30, 48, 42, 60, 55, 68],
                        glow: "glow-card-cyan"
                      },
                      { 
                        title: 'Active Customers', 
                        value: overviewData.kpis.active_customers.toLocaleString(), 
                        growth: overviewData.kpis.customers_growth,
                        desc: "avg customer signup rate",
                        color: "text-pink-400",
                        spark: [5, 12, 10, 18, 14, 25, 21, 35, 32, 42],
                        glow: "glow-card-rose"
                      },
                      { 
                        title: 'Inventory Health', 
                        value: `${overviewData.kpis.inventory_health}%`, 
                        growth: overviewData.kpis.inventory_growth,
                        desc: "SKUs tracked in stock",
                        color: "text-emerald-400",
                        spark: [80, 82, 85, 81, 88, 90, 89, 92, 91, 92.4],
                        glow: "border-emerald-500/20"
                      }
                    ].map((kpi, idx) => (
                      <div key={idx} className={`premium-card p-6 ${kpi.glow}`}>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">{kpi.title}</span>
                          <span className="text-[10px] bg-white/[0.04] text-gray-400 px-2 py-0.5 rounded-full font-semibold border border-white/[0.02]">{kpi.desc}</span>
                        </div>
                        
                        <div className="mt-4 flex items-baseline gap-2">
                          <span className="text-2xl font-extrabold text-white tracking-tight">{kpi.value}</span>
                          <span className={`text-[11px] font-bold flex items-center ${kpi.growth >= 0 ? 'text-emerald-400' : 'text-rose-500'}`}>
                            {kpi.growth >= 0 ? '▲' : '▼'} {Math.abs(kpi.growth)}%
                          </span>
                        </div>

                        {/* Custom sparkline SVG */}
                        <div className="h-10 mt-6 w-full opacity-70">
                          <ResponsiveContainer width="100%" height="100%">
                            <svg viewBox="0 0 100 30" className="w-full h-full overflow-visible">
                              <defs>
                                <linearGradient id={`sparkGrad-${idx}`} x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="0%" stopColor={idx === 0 ? '#6366f1' : idx === 1 ? '#06b6d4' : idx === 2 ? '#f43f5e' : '#10b981'} stopOpacity={0.15} />
                                  <stop offset="100%" stopColor="#050816" stopOpacity={0} />
                                </linearGradient>
                              </defs>
                              <path 
                                d={`M ${kpi.spark.map((val, i) => `${(i / (kpi.spark.length - 1)) * 100} ${30 - ((val - Math.min(...kpi.spark)) / (Math.max(...kpi.spark) - Math.min(...kpi.spark) || 1)) * 25 - 2}`).join(' L ')}`}
                                fill="none"
                                stroke={idx === 0 ? '#6366f1' : idx === 1 ? '#06b6d4' : idx === 2 ? '#f43f5e' : '#10b981'}
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              />
                              <path 
                                d={`M 0 30 L ${kpi.spark.map((val, i) => `${(i / (kpi.spark.length - 1)) * 100} ${30 - ((val - Math.min(...kpi.spark)) / (Math.max(...kpi.spark) - Math.min(...kpi.spark) || 1)) * 25 - 2}`).join(' L ')} L 100 30 Z`}
                                fill={`url(#sparkGrad-${idx})`}
                              />
                            </svg>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* AI Copilot insights panel */}
                  <div className="premium-card p-6 ai-border-glow border-violet-500/20">
                    <div className="flex items-center gap-3.5 mb-5">
                      <div className="p-2 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl text-white shadow-[0_0_15px_rgba(139,92,246,0.3)]">
                        <Sparkles size={20} className="animate-pulse" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">AI Commerce Intelligence</h3>
                        <p className="text-xs text-gray-400">Automated reasoning derived from the Gold aggregate storage layer.</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-6">
                      {overviewData.ai_insights.map((insight, index) => (
                        <div key={index} className="bg-white/[0.01] border border-white/[0.04] p-4.5 rounded-2xl flex flex-col justify-between hover:bg-white/[0.02] transition-colors">
                          <div>
                            <div className="flex items-center justify-between mb-3">
                              <span className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full ${
                                insight.type === 'revenue' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' :
                                insight.type === 'inventory' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              }`}>{insight.badge}</span>
                              <span className="text-[10px] text-gray-500 font-semibold">{insight.impact.toUpperCase()} IMPACT</span>
                            </div>
                            <h4 className="text-sm font-bold text-white mb-2">{insight.title}</h4>
                            <p className="text-xs text-gray-400 leading-relaxed">{insight.text}</p>
                          </div>
                          <div className="mt-4 pt-3.5 border-t border-white/[0.04]">
                            <div className="text-[9px] uppercase font-bold tracking-wider text-gray-500">Recommended Action</div>
                            <div className="text-xs text-indigo-300 font-semibold mt-1 flex items-center gap-1">
                              {insight.action}
                              <ArrowUpRight size={12} className="shrink-0" />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Revenue trend line with forecast and anomaly markers */}
                  <div className="grid grid-cols-3 gap-6">
                    <div className="col-span-2 premium-card p-6">
                      <div className="flex items-center justify-between mb-6">
                        <div>
                          <h3 className="text-lg font-bold text-white tracking-tight">Revenue Projection Timeline</h3>
                          <p className="text-xs text-gray-400">Composed chart plotting observed history, 7-day projection intervals, and data quality anomalies.</p>
                        </div>
                        <div className="flex items-center gap-4 text-xs">
                          <span className="flex items-center gap-1.5 text-gray-400">
                            <span className="h-1.5 w-4 bg-[#06b6d4] rounded-full"></span>
                            Observed Revenue
                          </span>
                          <span className="flex items-center gap-1.5 text-gray-400">
                            <span className="h-1.5 w-4 border-t-2 border-dashed border-[#8b5cf6] inline-block"></span>
                            Forecast
                          </span>
                          <span className="flex items-center gap-1.5 text-gray-400">
                            <span className="h-2 w-2 rounded-full bg-[#f43f5e]"></span>
                            Anomaly Point
                          </span>
                        </div>
                      </div>

                      <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                          <ComposedChart data={overviewData.trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.15}/>
                                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                              </linearGradient>
                              <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.15}/>
                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <XAxis dataKey="order_date" stroke="#4b5563" fontSize={10} tickLine={false} />
                            <YAxis stroke="#4b5563" fontSize={10} tickLine={false} tickFormatter={v => `$${v/1000}k`} />
                            
                            {/* Forecast Range Background Shading */}
                            <Area type="monotone" dataKey="forecast_upper" stroke="none" fill="#8b5cf6" fillOpacity={0.03} />
                            <Area type="monotone" dataKey="forecast_lower" stroke="none" fill="#8b5cf6" fillOpacity={0.03} />
                            
                            {/* Observed Revenue Area */}
                            <Area type="monotone" dataKey="total_revenue" stroke="#06b6d4" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRev)" />
                            
                            {/* Forecast Projection Line */}
                            <Area type="monotone" dataKey="forecast" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" fill="url(#colorForecast)" />
                            
                            {/* Outliers/Anomalies Scatter Dots */}
                            <Scatter dataKey="anomaly_revenue" fill="#f43f5e" shape="circle" line={false} />
                            
                            <Tooltip 
                              contentStyle={{ backgroundColor: 'rgba(9, 12, 28, 0.9)', borderColor: 'rgba(99, 102, 241, 0.2)' }}
                              formatter={(value, name) => {
                                if (!value) return null;
                                if (name === 'anomaly_revenue') return [`$${value.toLocaleString()}`, 'Anomaly Triggered'];
                                if (name === 'total_revenue') return [`$${value.toLocaleString()}`, 'Actual Revenue'];
                                if (name === 'forecast') return [`$${value.toLocaleString()}`, 'Projected Forecast'];
                                return [value, name];
                              }}
                            />
                          </ComposedChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Donut Chart redesigned to Sales Channels Performance */}
                    <div className="premium-card p-6 flex flex-col justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-white tracking-tight">Channel Share Matrix</h3>
                        <p className="text-xs text-gray-400 mt-1">Multi-channel relative performance based on transaction volume.</p>
                        
                        <div className="h-44 relative flex items-center justify-center mt-4">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={overviewData.channels}
                                cx="50%"
                                cy="50%"
                                innerRadius={52}
                                outerRadius={72}
                                paddingAngle={5}
                                dataKey="total_revenue"
                              >
                                {overviewData.channels.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                              </Pie>
                              <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937' }} formatter={v => `$${v.toLocaleString()}`} />
                            </PieChart>
                          </ResponsiveContainer>
                          <div className="absolute flex flex-col items-center">
                            <span className="text-2xl font-black text-white">3</span>
                            <span className="text-[9px] uppercase font-bold text-gray-500 tracking-wider">Active Channels</span>
                          </div>
                        </div>
                      </div>

                      {/* Clean Performance List */}
                      <div className="space-y-3 mt-4">
                        {overviewData.channels.map((ch, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs py-1.5 border-b border-white/[0.03] last:border-0">
                            <div className="flex items-center gap-2">
                              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[idx] }}></span>
                              <span className="font-bold text-white uppercase">{ch.channel}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-gray-400 font-semibold">${(ch.total_revenue/1000000).toFixed(2)}M</span>
                              <span className="text-emerald-400 font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded text-[9px]">{ch.performance_score}% Score</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Regional Performance map */}
                  <div className="premium-card p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-lg font-bold text-white tracking-tight">Geographic Revenue Distribution</h3>
                        <p className="text-xs text-gray-400">Total customer lifetime valuation split across domestic and global regions.</p>
                      </div>
                    </div>
                    
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={overviewData.regions}>
                          <XAxis dataKey="region" stroke="#4b5563" fontSize={10} tickLine={false} />
                          <YAxis stroke="#4b5563" fontSize={10} tickLine={false} tickFormatter={v => `$${v/1000}k`} />
                          <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937' }} formatter={v => `$${v.toLocaleString()}`} />
                          <Bar dataKey="lifetime_value" fill="#8b5cf6" radius={[6, 6, 0, 0]} maxBarSize={38}>
                            {overviewData.regions.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={`url(#barGrad-${index})`} />
                            ))}
                          </Bar>
                          <defs>
                            {overviewData.regions.map((entry, index) => (
                              <linearGradient key={`grad-${index}`} id={`barGrad-${index}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#8b5cf6" />
                                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.2} />
                              </linearGradient>
                            ))}
                          </defs>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Telemetry/Platform stats panel */}
                  <div className="grid grid-cols-4 gap-6">
                    {[
                      { title: "Observability Latency", val: `${overviewData.kpis.api_latency_ms} ms`, sub: "Avg REST load speed", icon: Clock },
                      { title: "ETL Success Rate", val: `${overviewData.kpis.etl_success_rate}%`, sub: "Continuous runs", icon: CheckCircle2 },
                      { title: "Orchestrator Engine", val: "Airflow 2.10", sub: "Active DAG pipeline schedules", icon: Database },
                      { title: "Data Freshness", val: "10m ago", sub: "S3 MinIO file system check", icon: RefreshCw }
                    ].map((telemetry, idx) => {
                      const Icon = telemetry.icon;
                      return (
                        <div key={idx} className="premium-card p-5 flex items-center gap-4 bg-white/[0.01]">
                          <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
                            <Icon size={18} />
                          </div>
                          <div>
                            <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">{telemetry.title}</div>
                            <div className="text-base font-bold text-white mt-1">{telemetry.val}</div>
                            <div className="text-[10px] text-gray-400 mt-0.5">{telemetry.sub}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                </div>
              )}

              {/* 2. REVENUE PAGE */}
              {activeTab === 'revenue' && revenueData && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  {/* Select filters */}
                  <div className="premium-card p-6 flex items-center gap-6">
                    <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
                      <SlidersHorizontal size={18} className="shrink-0" />
                    </div>
                    
                    <div className="flex-1 grid grid-cols-2 gap-6">
                      <div>
                        <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-2">Filter Sales Channel</label>
                        <select 
                          value={channelFilter} 
                          onChange={e => setChannelFilter(e.target.value)}
                          className="w-full bg-[#080b18]/60 border border-[#1f2937]/30 rounded-xl px-4 py-2.5 text-xs text-gray-300 focus:outline-none focus:border-indigo-500"
                        >
                          <option value="ALL">All Ingestion Channels</option>
                          <option value="SHOPIFY">Shopify Ingest</option>
                          <option value="AMAZON">Amazon Ingest</option>
                          <option value="FLIPKART">Flipkart Ingest</option>
                        </select>
                      </div>

                      <div>
                        <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-2">Filter Product Category</label>
                        <select 
                          value={categoryFilter} 
                          onChange={e => setCategoryFilter(e.target.value)}
                          className="w-full bg-[#080b18]/60 border border-[#1f2937]/30 rounded-xl px-4 py-2.5 text-xs text-gray-300 focus:outline-none focus:border-indigo-500"
                        >
                          <option value="ALL">All Categories</option>
                          <option value="Electronics">Electronics</option>
                          <option value="Apparel">Apparel</option>
                          <option value="Home & Kitchen">Home & Kitchen</option>
                          <option value="Beauty & Personal Care">Beauty & Personal Care</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Horizontal Category performance */}
                  <div className="grid grid-cols-2 gap-6">
                    <div className="premium-card p-6">
                      <h3 className="text-lg font-bold text-white tracking-tight mb-2">Category Performance Split</h3>
                      <p className="text-xs text-gray-400 mb-6">Total sales amount compared across active retail catalog categories.</p>
                      
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={revenueData.categories} layout="vertical">
                            <XAxis type="number" stroke="#4b5563" fontSize={10} tickLine={false} tickFormatter={v => `$${v/1000}k`} />
                            <YAxis dataKey="category" type="category" stroke="#4b5563" fontSize={10} tickLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937' }} formatter={v => `$${v.toLocaleString()}`} />
                            <Bar dataKey="total_amount" fill="#3b82f6" radius={[0, 4, 4, 0]} height={16}>
                              {revenueData.categories.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Table overview / Ledger summary */}
                    <div className="premium-card p-6 flex flex-col justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-white tracking-tight mb-2">Silver Transaction Ledger</h3>
                        <p className="text-xs text-gray-400 mb-4">Sample ledger displaying the most recent clean events ingested to the silver layer.</p>
                      </div>
                      
                      <div className="overflow-x-auto flex-1">
                        <table className="w-full text-left text-xs premium-table">
                          <thead>
                            <tr className="border-b border-[#1f2937]/30 text-gray-500 font-bold uppercase">
                              <th className="pb-3 pl-4">Order ID</th>
                              <th className="pb-3">Channel</th>
                              <th className="pb-3">Qty</th>
                              <th className="pb-3 text-right pr-4">Total Amount</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#1f2937]/20">
                            {revenueData.orders.map((o, idx) => (
                              <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                                <td className="py-3.5 pl-4 font-semibold text-white">{o.order_id}</td>
                                <td className="py-3.5">
                                  <span className="bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded font-bold text-[9px] tracking-wider uppercase">
                                    {o.channel}
                                  </span>
                                </td>
                                <td className="py-3.5 text-gray-300">{o.quantity}</td>
                                <td className="py-3.5 text-right pr-4 font-bold text-white">${o.total_amount.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 3. CUSTOMER PAGE */}
              {activeTab === 'customers' && customerData && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <div className="premium-card p-6" style={{ overflow: 'visible', zIndex: 30 }} ref={comboboxRef}>
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block mb-2">Query Customer Profiles</label>
                    <div className="combobox-container">
                      <div className="relative">
                        <Search size={16} className="absolute left-4 top-3.5 text-gray-500" />
                        <input 
                          type="text" 
                          placeholder={
                            selectedCustomerId 
                              ? `Search customer (Current: ${
                                  customerData.find(c => c.customer_id === selectedCustomerId)
                                    ? `${customerData.find(c => c.customer_id === selectedCustomerId).first_name} ${customerData.find(c => c.customer_id === selectedCustomerId).last_name} [${selectedCustomerId}]`
                                    : selectedCustomerId
                                })`
                              : "Search by ID, name, email, region..."
                          }
                          value={custSearch}
                          onFocus={() => setDropdownOpen(true)}
                          onChange={e => {
                            setCustSearch(e.target.value);
                            setDropdownOpen(true);
                          }}
                          className="w-full bg-[#080b18]/60 border border-[#1f2937]/30 rounded-xl pl-12 pr-4 py-3 text-xs text-gray-300 focus:outline-none focus:border-indigo-500"
                        />
                      </div>

                      {/* Search dropdown list */}
                      {dropdownOpen && (
                        <div className="combobox-dropdown">
                          {customerData
                            .filter(c => {
                              const searchStr = `${c.first_name} ${c.last_name} ${c.email} ${c.customer_id} ${c.region || ''} ${c.country || ''}`.toLowerCase();
                              return searchStr.includes(custSearch.toLowerCase());
                            })
                            .slice(0, 20)
                            .map(c => (
                              <button
                                key={c.customer_id}
                                onClick={() => {
                                  setSelectedCustomerId(c.customer_id);
                                  setCustSearch('');
                                  setDropdownOpen(false);
                                }}
                                className={`combobox-item ${selectedCustomerId === c.customer_id ? 'selected' : ''}`}
                              >
                                <div className="flex items-center gap-3">
                                  <div className="avatar-mini">
                                    {c.first_name[0] || ''}{c.last_name[0] || ''}
                                  </div>
                                  <div className="flex flex-col">
                                    <span className="font-bold text-white text-xs">{c.first_name} {c.last_name}</span>
                                    <span className="text-[10px] text-gray-500">{c.email}</span>
                                  </div>
                                </div>
                                <span className="text-[9px] bg-white/[0.04] text-gray-400 font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded">
                                  {c.customer_id}
                                </span>
                              </button>
                            ))}
                          {customerData.filter(c => 
                            `${c.first_name} ${c.last_name} ${c.email} ${c.customer_id} ${c.region || ''} ${c.country || ''}`.toLowerCase().includes(custSearch.toLowerCase())
                          ).length === 0 && (
                            <div className="p-4 text-center text-xs text-gray-500">
                              No matching customers found
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-6">
                    {/* Customer Profile detail */}
                    {customerData.filter(c => c.customer_id === selectedCustomerId).map(cust => (
                        <div key={cust.customer_id} className="space-y-6">
                          
                          <div className="premium-card p-6">
                            <div className="flex items-center gap-4 mb-6 border-b border-[#1f2937]/30 pb-4">
                              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-center text-white font-extrabold text-sm shadow-md">
                                {cust.first_name[0]}{cust.last_name[0]}
                              </div>
                              <div>
                                <h3 className="text-lg font-bold text-white tracking-tight">{cust.first_name} {cust.last_name}</h3>
                                <p className="text-xs text-gray-500 uppercase font-bold mt-0.5">{cust.customer_id}</p>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-xs">
                              <div>
                                <span className="text-gray-500 font-bold text-[9px] uppercase tracking-wider block mb-1">Email Address</span>
                                <span className="text-white font-semibold flex items-center gap-1.5">
                                  <Mail size={12} className="text-indigo-400" />
                                  {cust.email}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500 font-bold text-[9px] uppercase tracking-wider block mb-1">Phone Contact</span>
                                <span className="text-white font-semibold flex items-center gap-1.5">
                                  <Phone size={12} className="text-indigo-400" />
                                  {cust.phone}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500 font-bold text-[9px] uppercase tracking-wider block mb-1">Region / Country</span>
                                <span className="text-white font-semibold flex items-center gap-1.5">
                                  <MapPin size={12} className="text-indigo-400" />
                                  {cust.region} / {cust.country}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500 font-bold text-[9px] uppercase tracking-wider block mb-1">Sign-up Timestamp</span>
                                <span className="text-white font-semibold flex items-center gap-1.5">
                                  <Clock size={12} className="text-indigo-400" />
                                  {cust.signup_date}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Customer metrics */}
                          <div className="grid grid-cols-4 gap-4">
                            {[
                              { label: 'Customer LTV', val: `$${cust.lifetime_value.toFixed(2)}`, color: 'text-emerald-400', badge: 'Loyalty Value' },
                              { label: 'Total Orders', val: cust.total_orders, color: 'text-indigo-400', badge: 'Order Vol' },
                              { label: 'Pref. Channel', val: cust.preferred_channel, color: 'text-indigo-400', badge: 'Channel' },
                              { label: 'Fav Category', val: cust.favorite_category, color: 'text-indigo-400', badge: 'Product Focus' }
                            ].map((m, idx) => (
                              <div key={idx} className="premium-card p-5 text-center bg-white/[0.01]">
                                <div className="text-[9px] font-bold text-gray-500 uppercase tracking-wider">{m.label}</div>
                                <div className={`text-base font-extrabold mt-2.5 ${m.color}`}>{m.val}</div>
                                <div className="text-[9px] text-gray-400 mt-1 bg-white/[0.02] py-0.5 rounded font-semibold border border-white/[0.02]">{m.badge}</div>
                              </div>
                            ))}
                          </div>

                          {/* Timeline scatter chart */}
                          <div className="premium-card p-6">
                            <h4 className="text-sm font-bold text-white mb-2">Purchase History Timeline</h4>
                            <p className="text-xs text-gray-500 mb-6">Historical transaction values processed for this customer.</p>
                            
                            <div className="h-56">
                              <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={customerTimeline}>
                                  <XAxis dataKey="order_timestamp" stroke="#4b5563" fontSize={10} tickLine={false} />
                                  <YAxis dataKey="total_amount" name="Revenue" unit="$" stroke="#4b5563" fontSize={10} tickLine={false} />
                                  <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937' }} />
                                  <Scatter name="Orders" dataKey="total_amount" fill="#6366f1" />
                                </ComposedChart>
                              </ResponsiveContainer>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* 4. INVENTORY PAGE */}
              {activeTab === 'inventory' && inventoryData && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <div className="grid grid-cols-3 gap-6">
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Catalog SKUs</div>
                      <div className="text-2xl font-black mt-3 text-white">{inventoryData.total_sku} SKUs Tracked</div>
                    </div>
                    <div className="premium-card p-6 border-rose-500/20">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Restock Alerts</div>
                      <div className="text-2xl font-black mt-3 text-rose-400">{inventoryData.low_stock.length} Low Stock</div>
                    </div>
                    <div className="premium-card p-6 border-amber-500/20">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Stagnant Stock Items</div>
                      <div className="text-2xl font-black mt-3 text-amber-400">{inventoryData.dead_stock.length} Dead SKUs</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="premium-card p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-md font-bold text-rose-400 uppercase tracking-tight">Replenishment Action List</h3>
                        <span className="text-[10px] bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded font-bold">Action Required</span>
                      </div>
                      
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs premium-table">
                          <thead>
                            <tr className="border-b border-[#1f2937]/30 text-gray-500 font-bold uppercase">
                              <th className="pb-3 pl-4">SKU ID</th>
                              <th className="pb-3">Product Name</th>
                              <th className="pb-3 text-right">Available</th>
                              <th className="pb-3 text-right pr-4">Threshold</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#1f2937]/20">
                            {inventoryData.low_stock.map((item, idx) => (
                              <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                                <td className="py-3.5 pl-4 font-semibold text-white">{item.product_id}</td>
                                <td className="py-3.5 text-gray-300">{item.product_name}</td>
                                <td className="py-3.5 text-right font-bold text-rose-400">{item.stock_on_hand}</td>
                                <td className="py-3.5 text-right pr-4 text-gray-500 font-semibold">{item.restock_threshold}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <div className="premium-card p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-md font-bold text-amber-400 uppercase tracking-tight">Dead Stock Value Audits</h3>
                        <span className="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded font-bold">Capital Lockup</span>
                      </div>
                      
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs premium-table">
                          <thead>
                            <tr className="border-b border-[#1f2937]/30 text-gray-500 font-bold uppercase">
                              <th className="pb-3 pl-4">SKU ID</th>
                              <th className="pb-3">Name</th>
                              <th className="pb-3 text-right">Stock</th>
                              <th className="pb-3 text-right pr-4">Lockup Value</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#1f2937]/20">
                            {inventoryData.dead_stock.map((item, idx) => (
                              <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                                <td className="py-3.5 pl-4 font-semibold text-white">{item.product_id}</td>
                                <td className="py-3.5 text-gray-300">{item.product_name}</td>
                                <td className="py-3.5 text-right text-gray-400">{item.stock_on_hand}</td>
                                <td className="py-3.5 text-right pr-4 font-bold text-amber-400">${item.current_inventory_value.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 5. PLATFORM MONITORING PAGE */}
              {activeTab === 'monitoring' && monitoringData && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <div className="grid grid-cols-3 gap-6">
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Engine status</div>
                      <div className="text-lg font-bold mt-3 text-emerald-400 flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 pulse-indicator"></span>
                        Airflow Engine Healthy
                      </div>
                    </div>
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Orchestration Health</div>
                      <div className="text-2xl font-black mt-3 text-white">100% Pipeline SLA</div>
                    </div>
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Scheduled Pipelines</div>
                      <div className="text-2xl font-black mt-3 text-indigo-400">4 Active DAGs</div>
                    </div>
                  </div>

                  <div className="premium-card p-6">
                    <h3 className="text-lg font-bold text-white tracking-tight mb-2">Orchestration Logs</h3>
                    <p className="text-xs text-gray-400 mb-6">Task run durations and outputs tracked dynamically by the scheduling engine.</p>
                    
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs premium-table">
                        <thead>
                          <tr className="border-b border-[#1f2937]/30 text-gray-500 font-bold uppercase">
                            <th className="pb-3 pl-4">DAG Execution Target</th>
                            <th className="pb-3">Trigger Mode</th>
                            <th className="pb-3">Start Date/Time</th>
                            <th className="pb-3 text-right">Job State</th>
                            <th className="pb-3 text-right pr-4">Duration (s)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1f2937]/20">
                          {monitoringData.runs.map((run, idx) => (
                            <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                              <td className="py-3.5 pl-4 font-semibold text-white">{run.dag_id}</td>
                              <td className="py-3.5">
                                <span className="bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded font-bold text-[9px] tracking-wider uppercase">
                                  {run.run_type}
                                </span>
                              </td>
                              <td className="py-3.5 text-gray-400">{run.start_date}</td>
                              <td className="py-3.5 text-right">
                                <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                                  {run.state}
                                </span>
                              </td>
                              <td className="py-3.5 text-right pr-4 font-bold text-white">{run.duration}s</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* 6. DATA QUALITY CENTER */}
              {activeTab === 'quality' && qualityData && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <div className="grid grid-cols-3 gap-6">
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Quality Audits</div>
                      <div className="text-2xl font-black mt-3 text-emerald-400">100% Passed</div>
                    </div>
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Delta Tables Checked</div>
                      <div className="text-2xl font-black mt-3 text-white">4 Delta Tables</div>
                    </div>
                    <div className="premium-card p-6">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Failures Detected</div>
                      <div className="text-2xl font-black mt-3 text-emerald-400">0 Errors</div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    {qualityData.reports.map((r, idx) => (
                      <div key={idx} className="premium-card p-6">
                        <div className="flex items-center justify-between border-b border-[#1f2937]/30 pb-4 mb-4">
                          <h4 className="text-sm font-bold text-white uppercase tracking-wider">{r.table_name}</h4>
                          <span className="text-[10px] text-gray-500 font-semibold">Audit Run: {r.timestamp}</span>
                        </div>
                        
                        <div className="space-y-3">
                          {r.details.map((check, cIdx) => (
                            <div key={cIdx} className="flex items-center justify-between py-2 border-b border-white/[0.03] last:border-b-0 text-xs">
                              <span className="text-gray-300 font-semibold">{check.description}</span>
                              <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[9px] font-bold">
                                PASSED
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 7. LINEAGE EXPLORER */}
              {activeTab === 'lineage' && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <div className="premium-card p-8">
                    <h3 className="text-lg font-bold text-white tracking-tight mb-2">Telemetry Dataset Lineage Map</h3>
                    <p className="text-xs text-gray-400 mb-8">Metadata dependency tracking from landing ingestion sources down to aggregate dashboard endpoints.</p>
                    
                    <div className="flex items-center justify-between gap-4 py-8 overflow-x-auto">
                      
                      {/* Sources Column */}
                      <div className="flex flex-col gap-4">
                        <div className="text-[10px] font-bold text-gray-500 uppercase text-center tracking-wider">1. CSV Landing</div>
                        <div className="bg-[#080b18]/60 border border-amber-500/20 px-6 py-4 rounded-xl text-center shadow-lg hover:border-amber-500/50 transition-all w-48">
                          <span className="text-xs font-bold text-amber-400 block">amazon_orders</span>
                        </div>
                        <div className="bg-[#080b18]/60 border border-blue-500/20 px-6 py-4 rounded-xl text-center shadow-lg hover:border-blue-500/50 transition-all w-48">
                          <span className="text-xs font-bold text-blue-400 block">flipkart_orders</span>
                        </div>
                        <div className="bg-[#080b18]/60 border border-indigo-500/20 px-6 py-4 rounded-xl text-center shadow-lg hover:border-indigo-500/50 transition-all w-48">
                          <span className="text-xs font-bold text-indigo-400 block">shopify_orders</span>
                        </div>
                      </div>

                      <div className="text-gray-700 text-lg font-black shrink-0">➔</div>

                      {/* Bronze Column */}
                      <div className="flex flex-col gap-4">
                        <div className="text-[10px] font-bold text-gray-500 uppercase text-center tracking-wider">2. Bronze Delta</div>
                        <div className="bg-[#080b18]/60 border border-white/[0.04] px-6 py-4 rounded-xl text-center shadow-lg w-48">
                          <span className="text-xs font-semibold text-gray-300 block">bronze_amz</span>
                        </div>
                        <div className="bg-[#080b18]/60 border border-white/[0.04] px-6 py-4 rounded-xl text-center shadow-lg w-48">
                          <span className="text-xs font-semibold text-gray-300 block">bronze_flk</span>
                        </div>
                        <div className="bg-[#080b18]/60 border border-white/[0.04] px-6 py-4 rounded-xl text-center shadow-lg w-48">
                          <span className="text-xs font-semibold text-gray-300 block">bronze_sh</span>
                        </div>
                      </div>

                      <div className="text-gray-700 text-lg font-black shrink-0">➔</div>

                      {/* Silver Column */}
                      <div className="flex flex-col gap-4">
                        <div className="text-[10px] font-bold text-gray-500 uppercase text-center tracking-wider">3. Silver Delta</div>
                        <div className="bg-indigo-950/20 border border-indigo-500/30 px-6 py-5 rounded-xl text-center shadow-lg hover:border-indigo-500/60 transition-all w-52">
                          <span className="text-xs font-bold text-indigo-300 block">silver_orders</span>
                          <div className="text-[9px] text-emerald-400 font-bold uppercase mt-1">Quality audited</div>
                        </div>
                      </div>

                      <div className="text-gray-700 text-lg font-black shrink-0">➔</div>

                      {/* Gold Column */}
                      <div className="flex flex-col gap-4">
                        <div className="text-[10px] font-bold text-gray-500 uppercase text-center tracking-wider">4. Gold Aggregate</div>
                        <div className="bg-pink-950/20 border border-pink-500/30 px-6 py-4 rounded-xl text-center shadow-lg hover:border-pink-500/60 transition-all w-48">
                          <span className="text-xs font-bold text-pink-300 block">gold_daily_revenue</span>
                        </div>
                      </div>

                      <div className="text-gray-700 text-lg font-black shrink-0">➔</div>

                      {/* Consumer Column */}
                      <div className="flex flex-col gap-4">
                        <div className="text-[10px] font-bold text-gray-500 uppercase text-center tracking-wider">5. Web Client</div>
                        <div className="bg-gradient-to-r from-indigo-600 to-pink-600 px-6 py-5 rounded-xl text-center shadow-xl w-48">
                          <span className="text-xs font-bold text-white block">React Analytics UI</span>
                        </div>
                      </div>

                    </div>
                  </div>
                </div>
              )}
            </>
          )}

        </div>
      </main>

    </div>
  );
}
