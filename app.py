import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CodeNova | Sales Analytics", page_icon="📊", layout="wide")

st.title("📊 Sales Performance Analytics Dashboard")
st.caption("Developed as part of CodeNova Data Science Internship | Python, Pandas, Streamlit & Plotly")

REQUIRED_COLUMNS = [
    "Order_ID", "Order_Date", "Product", "Category", "Region",
    "Sales_Channel", "Customer_Type", "Quantity", "Unit_Price_INR",
    "Unit_Cost_INR", "Discount_Percent", "Payment_Method"
]

def prepare_data(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce", dayfirst=True)
    numeric_cols = [
        "Quantity", "Unit_Price_INR", "Unit_Cost_INR", "Discount_Percent"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=[
        "Order_Date", "Quantity", "Unit_Price_INR",
        "Unit_Cost_INR", "Discount_Percent"
    ])

    # Task 1 dataset stores discount as a fraction (for example, 0.15 = 15%).
    # Convert whole-number percentages such as 15 to 0.15 if present.
    if not df.empty and df["Discount_Percent"].max() > 1:
        df["Discount_Percent"] = df["Discount_Percent"] / 100

    df["Gross_Sales"] = df["Quantity"] * df["Unit_Price_INR"]
    df["Discount_Amount"] = df["Gross_Sales"] * df["Discount_Percent"]
    df["Net_Sales"] = df["Gross_Sales"] - df["Discount_Amount"]
    df["Total_Cost"] = df["Quantity"] * df["Unit_Cost_INR"]
    df["Profit"] = df["Net_Sales"] - df["Total_Cost"]
    df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Discount_Rate"] = df["Discount_Percent"] * 100
    return df

uploaded = st.sidebar.file_uploader("Upload your CodeNova Task 1 CSV file", type=["csv"])
default_file = Path("Copy of codenova_sales_sample.csv")

try:
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
    elif default_file.exists():
        raw = pd.read_csv(default_file)
        st.sidebar.success(f"Loaded: {default_file.name}")
    else:
        st.info("Upload your Task 1 CSV file from the left sidebar to display the dashboard.")
        st.markdown(
            "**Expected file:** `Copy of codenova_sales_sample.csv`  \n"
            "The CSV should contain the 12 Task 1 columns, including `Order_ID`, "
            "`Order_Date`, `Product`, `Category`, `Region`, `Quantity`, "
            "`Unit_Price_INR`, `Unit_Cost_INR`, and `Discount_Percent`."
        )
        st.stop()

    data = prepare_data(raw)
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

if data.empty:
    st.warning("The uploaded file has no valid rows after cleaning.")
    st.stop()

st.sidebar.header("🔎 Dashboard Filters")
min_date = data["Order_Date"].min().date()
max_date = data["Order_Date"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = data[
    (data["Order_Date"].dt.date >= start_date) &
    (data["Order_Date"].dt.date <= end_date)
]

filter_columns = ["Category", "Region", "Product", "Sales_Channel", "Customer_Type"]
for col in filter_columns:
    options = sorted(filtered[col].dropna().astype(str).unique().tolist())
    selected = st.sidebar.multiselect(f"Select {col.replace('_', ' ')}", options, default=options)
    filtered = filtered[filtered[col].astype(str).isin(selected)]

if filtered.empty:
    st.warning("No records match the selected filters. Change or clear the filters.")
    st.stop()

# KPI cards
total_sales = filtered["Net_Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order_ID"].nunique()
avg_order_value = total_sales / total_orders if total_orders else 0
profit_margin = (total_profit / total_sales * 100) if total_sales else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Net Revenue", f"₹{total_sales:,.0f}")
c2.metric("Total Profit", f"₹{total_profit:,.0f}")
c3.metric("Total Orders", f"{total_orders:,}")
c4.metric("Average Order Value", f"₹{avg_order_value:,.0f}")
c5.metric("Profit Margin", f"{profit_margin:.1f}%")

st.divider()

left, right = st.columns(2)
with left:
    st.subheader("Monthly Revenue Trend")
    monthly = filtered.groupby("Month", as_index=False)["Net_Sales"].sum()
    fig = px.line(monthly, x="Month", y="Net_Sales", markers=True,
                  labels={"Net_Sales": "Net Revenue (₹)", "Month": "Month"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Revenue by Category")
    category = filtered.groupby("Category", as_index=False)["Net_Sales"].sum()
    fig = px.bar(category, x="Category", y="Net_Sales", color="Category",
                 labels={"Net_Sales": "Net Revenue (₹)"})
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Profit by Region")
    region = filtered.groupby("Region", as_index=False)["Profit"].sum()
    fig = px.bar(region, x="Region", y="Profit", color="Region",
                 labels={"Profit": "Profit (₹)"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Sales vs Profit")
    fig = px.scatter(filtered, x="Net_Sales", y="Profit", color="Category",
                     hover_data=["Product", "Region", "Order_ID"],
                     labels={"Net_Sales": "Net Revenue (₹)", "Profit": "Profit (₹)"})
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Revenue by Sales Channel")
    channel = filtered.groupby("Sales_Channel", as_index=False)["Net_Sales"].sum()
    fig = px.pie(channel, names="Sales_Channel", values="Net_Sales", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top 10 Products by Revenue")
    products = (filtered.groupby("Product", as_index=False)["Net_Sales"]
                .sum().sort_values("Net_Sales", ascending=False).head(10))
    fig = px.bar(products.sort_values("Net_Sales"), x="Net_Sales", y="Product",
                 orientation="h", labels={"Net_Sales": "Net Revenue (₹)"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtered Sales Records")
display_cols = [
    "Order_ID", "Order_Date", "Product", "Category", "Region",
    "Quantity", "Gross_Sales", "Discount_Amount", "Net_Sales",
    "Total_Cost", "Profit"
]
st.dataframe(filtered[display_cols].sort_values("Order_Date", ascending=False),
             use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data as CSV", csv,
                   "codenova_filtered_sales.csv", "text/csv")

st.caption("Calculation: Net Revenue = Quantity × Unit Price − Discount; "
           "Profit = Net Revenue − (Quantity × Unit Cost).")
