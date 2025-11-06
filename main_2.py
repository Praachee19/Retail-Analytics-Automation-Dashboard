import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Performance & Inventory Dashboard", layout="wide")

st.title("Retail Sales & Inventory Dashboard")
st.caption("Automated insights from national to SKU level")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload your retail dataset CSV file", type=["csv"])

df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"])

    # --- Simulate inventory level and reorder level ---
    if "Inventory_Level" not in df.columns:
        df["Inventory_Level"] = (df["Quantity"] * 10).astype(int)
        df["Reorder_Level"] = 100
        df["Alert_Color"] = df["Inventory_Level"].apply(
            lambda x: "Green" if x > 100 else ("Orange" if x == 100 else "Red")
        )

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    filtered_df = df.copy()

    region_options = ["All"] + sorted(filtered_df["Region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Region", region_options)

    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]

    state_options = ["All"] + sorted(filtered_df["State"].unique().tolist())
    selected_state = st.sidebar.selectbox("State", state_options)

    if selected_state != "All":
        filtered_df = filtered_df[filtered_df["State"] == selected_state]

    subcat_options = ["All"] + sorted(filtered_df["Sub_Category"].unique().tolist())
    selected_subcat = st.sidebar.selectbox("Sub Category", subcat_options)

    if selected_subcat != "All":
        filtered_df = filtered_df[filtered_df["Sub_Category"] == selected_subcat]

    product_options = ["All"] + sorted(filtered_df["Product_Name"].unique().tolist())
    selected_product = st.sidebar.selectbox("Product", product_options)

    if selected_product != "All":
        filtered_df = filtered_df[filtered_df["Product_Name"] == selected_product]

    sku_options = ["All"] + sorted(filtered_df["SKU"].unique().tolist())
    selected_sku = st.sidebar.selectbox("SKU", sku_options)

    if selected_sku != "All":
        filtered_df = filtered_df[filtered_df["SKU"] == selected_sku]

    # --- KPIs ---
    total_sales = filtered_df["Sales"].sum()
    total_profit = filtered_df["Profit"].sum()
    total_stores = filtered_df["Store_Code"].nunique()

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Sales", f"${total_sales:,.0f}")
    kpi2.metric("Total Profit", f"${total_profit:,.0f}")
    kpi3.metric("Active Stores", total_stores)

    # --- Charts ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Sales by Region",
        "Category Breakdown",
        "Monthly Trend",
        "Inventory Alerts"
    ])

    with tab1:
        region_sales = filtered_df.groupby("Region", as_index=False)["Sales"].sum()
        fig1 = px.bar(region_sales, x="Region", y="Sales", title="Sales by Region", color="Region")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        category_sales = filtered_df.groupby("Sub_Category", as_index=False)["Sales"].sum()
        fig2 = px.pie(category_sales, names="Sub_Category", values="Sales", title="Sales by Sub Category")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        monthly_sales = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Sales"].sum().reset_index()
        monthly_sales["Date"] = monthly_sales["Date"].astype(str)
        fig3 = px.line(monthly_sales, x="Date", y="Sales", markers=True, title="Monthly Sales Trend")
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        alert_summary = filtered_df.groupby(["Store_Code", "Product_Name", "SKU", "Alert_Color"], as_index=False)[
            ["Inventory_Level", "Reorder_Level"]
        ].mean()
        st.dataframe(alert_summary)

        color_counts = filtered_df["Alert_Color"].value_counts().reset_index()
        color_counts.columns = ["Alert_Color", "Count"]
        fig4 = px.bar(color_counts, x="Alert_Color", y="Count", color="Alert_Color",
                      title="Inventory Alert Levels")
        st.plotly_chart(fig4, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.info("To refresh, replace the dataset in the 'output' folder and click Rerun.")

else:
    st.info("Please upload a CSV file to see the dashboard.")