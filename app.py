import streamlit as st
import pandas as pd
import sqlite3

# ── Page Config ──
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# ── Load Data ──
@st.cache_data
def load_data():
    conn = sqlite3.connect("output/sales.db")
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

# ── Title ──
st.title("📊 E-Commerce Sales Dashboard")

# ── Sidebar Filters ──
st.sidebar.header("Filters")

selected_country = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].dropna().unique(),
    default=df["Country"].dropna().unique()
)

selected_day = st.sidebar.multiselect(
    "Select Day of Week",
    options=df["DayOfWeek"].dropna().unique(),
    default=df["DayOfWeek"].dropna().unique()
)

# Apply filters
filtered_df = df[
    (df["Country"].isin(selected_country)) &
    (df["DayOfWeek"].isin(selected_day))
]

# ── KPIs ──
total_rev     = filtered_df["Revenue"].sum()
total_orders  = filtered_df["InvoiceNo"].nunique()
total_cust    = filtered_df["CustomerID"].nunique()
avg_order_val = filtered_df.groupby("InvoiceNo")["Revenue"].sum().mean()

top_country = (
    filtered_df.groupby("Country")["Revenue"]
    .sum().idxmax() if not filtered_df.empty else "N/A"
)

top_product = (
    filtered_df.groupby("Description")["Revenue"]
    .sum().idxmax() if not filtered_df.empty else "N/A"
)

# KPI Layout
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Revenue", f"£{total_rev:,.0f}")
col2.metric("Orders", f"{total_orders}")
col3.metric("Customers", f"{total_cust}")
col4.metric("Avg Order Value", f"£{avg_order_val:,.2f}" if not pd.isna(avg_order_val) else "0")
col5.metric("Top Country", top_country)

# ── Charts ──

# 1. Monthly Revenue Trend
st.subheader("📈 Monthly Revenue Trend")
monthly = filtered_df.groupby("Month")["Revenue"].sum()
st.line_chart(monthly)

# 2. Top Countries
colA, colB = st.columns(2)

with colA:
    st.subheader("🌍 Top Countries")
    top_countries = (
        filtered_df.groupby("Country")["Revenue"]
        .sum().sort_values(ascending=False).head(10)
    )
    st.bar_chart(top_countries)

# 3. Top Products
with colB:
    st.subheader("🛒 Top Products")
    top_products = (
        filtered_df.groupby("Description")["Revenue"]
        .sum().sort_values(ascending=False).head(10)
    )
    st.bar_chart(top_products)
filtered_df = filtered_df.copy()
# 4. Orders by Day
st.subheader("📅 Orders by Day of Week")
dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow = filtered_df.groupby("DayOfWeek")["InvoiceNo"].nunique().reindex(dow_order)
st.bar_chart(dow)

# 5. Quantity Distribution
st.subheader("📦 Revenue by Quantity Bucket")

bins = [0, 5, 20, 100, float("inf")]
labels = ["1-5", "6-20", "21-100", "100+"]

filtered_df["QtyBucket"] = pd.cut(filtered_df["Quantity"], bins=bins, labels=labels)

qty_rev = filtered_df.groupby("QtyBucket", observed=True)["Revenue"].sum()

# ── Data Preview ──
st.subheader("🔍 Raw Data")
st.dataframe(filtered_df.head(100))
