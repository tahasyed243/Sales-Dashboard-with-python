# Assignment 02 - Business Intelligence & Data Visualization
# Streamlit Web Dashboard

import streamlit as st
import pandas as pd

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ---------------------------
# Cache Data Loading
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    return df

# ---------------------------
# Load Data
# ---------------------------
df = load_data()

# ---------------------------
# Data Preprocessing
# ---------------------------
df.fillna(0, inplace=True)

# Safe date conversion
df['Order Date'] = pd.to_datetime(
    df['Order Date'],
    errors='coerce',
    dayfirst=True
)

df = df.dropna(subset=['Order Date'])

df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month_name()
df['Profit %'] = (df['Profit'] / df['Sales']) * 100

# ---------------------------
# Title & Description
# ---------------------------
st.title("📊 STK || Sales Performance Dashboard")
st.write("This dashboard analyzes sales, profit, and performance trends using an interactive Streamlit web app.")

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.title("STK Dashboard")
st.sidebar.header("Filters")

start_date = st.sidebar.date_input("Start Date", df['Order Date'].min())
end_date = st.sidebar.date_input("End Date", df['Order Date'].max())

category = st.sidebar.multiselect(
    "Select Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

sales_range = st.sidebar.slider(
    "Sales Range",
    float(df['Sales'].min()),
    float(df['Sales'].max()),
    (float(df['Sales'].min()), float(df['Sales'].max()))
)

# ---------------------------
# Apply Filters
# ---------------------------
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(start_date)) &
    (df['Order Date'] <= pd.to_datetime(end_date)) &
    (df['Category'].isin(category)) &
    (df['Region'].isin(region)) &
    (df['Sales'] >= sales_range[0]) &
    (df['Sales'] <= sales_range[1])
]

# ---------------------------
# KPI Metrics
# ---------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("Average Order Value", f"${filtered_df['Sales'].mean():,.0f}")

# ---------------------------
# Charts (Streamlit Native)
# ---------------------------
colA, colB = st.columns(2)

# Line Chart - Monthly Sales
with colA:
    st.subheader("Monthly Sales Trend")
    monthly_sales = filtered_df.groupby(
        filtered_df['Order Date'].dt.to_period('M')
    )['Sales'].sum()
    monthly_sales.index = monthly_sales.index.astype(str)
    st.line_chart(monthly_sales)

# Bar Chart - Category Sales
with colB:
    st.subheader("Category-wise Sales")
    category_sales = filtered_df.groupby('Category')['Sales'].sum()
    st.bar_chart(category_sales)

# ---------------------------
# Region Sales (Table instead of Pie)
# ---------------------------
st.subheader("Sales by Region")
region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
st.dataframe(region_sales)

# ---------------------------
# Top 10 Products
# ---------------------------
st.subheader("Top 10 Products by Sales")
top_10 = (
    filtered_df
    .groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.dataframe(top_10.reset_index())
