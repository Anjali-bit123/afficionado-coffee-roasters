import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Afficionado Coffee Roasters | Product & Revenue Analysis",
    page_icon="☕",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "Afficionado Coffee Roasters.xlsx"

REQUIRED_COLUMNS = [
    "transaction_id", "year", "transaction_time", "transaction_qty",
    "store_id", "store_location", "product_id", "unit_price",
    "product_category", "product_type", "product_detail"
]

@st.cache_data
def load_data():
    data = pd.read_excel(DATA_FILE)
    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    data = data.copy()
    data["transaction_qty"] = pd.to_numeric(data["transaction_qty"], errors="coerce")
    data["unit_price"] = pd.to_numeric(data["unit_price"], errors="coerce")
    data = data.dropna(subset=[
        "transaction_id", "transaction_qty", "unit_price",
        "product_category", "product_type", "product_detail"
    ])
    data = data[(data["transaction_qty"] > 0) & (data["unit_price"] >= 0)]
    data["revenue"] = data["transaction_qty"] * data["unit_price"]
    return data

st.title("☕ Product Optimization & Revenue Contribution Analysis")
st.caption("Afficionado Coffee Roasters | Interactive product and category performance dashboard")

try:
    df = load_data()
except Exception as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")
years = sorted(df["year"].dropna().unique().tolist())
categories = sorted(df["product_category"].dropna().unique().tolist())
stores = sorted(df["store_location"].dropna().unique().tolist())

selected_years = st.sidebar.multiselect("Year", years, default=years)
selected_categories = st.sidebar.multiselect("Product category", categories, default=categories)
selected_stores = st.sidebar.multiselect("Store location", stores, default=stores)

filtered = df[
    df["year"].isin(selected_years)
    & df["product_category"].isin(selected_categories)
    & df["store_location"].isin(selected_stores)
].copy()

if filtered.empty:
    st.warning("No transactions match the selected filters. Please change the filters.")
    st.stop()

# Aggregations
total_revenue = filtered["revenue"].sum()
total_units = filtered["transaction_qty"].sum()
transaction_count = filtered["transaction_id"].nunique()
avg_transaction_revenue = total_revenue / transaction_count if transaction_count else 0

product = (
    filtered.groupby(["product_id", "product_category", "product_type", "product_detail"], as_index=False)
    .agg(units_sold=("transaction_qty", "sum"),
         total_revenue=("revenue", "sum"),
         transactions=("transaction_id", "nunique"))
)
product["revenue_share_pct"] = (
    product["total_revenue"] / total_revenue * 100 if total_revenue else 0
)
product["sales_rank"] = product["units_sold"].rank(method="min", ascending=False).astype(int)
product["revenue_rank"] = product["total_revenue"].rank(method="min", ascending=False).astype(int)

category = (
    filtered.groupby("product_category", as_index=False)
    .agg(units_sold=("transaction_qty", "sum"),
         total_revenue=("revenue", "sum"),
         transactions=("transaction_id", "nunique"))
)
category["revenue_share_pct"] = (
    category["total_revenue"] / total_revenue * 100 if total_revenue else 0
)
category = category.sort_values("total_revenue", ascending=False)

ptype = (
    filtered.groupby(["product_category", "product_type"], as_index=False)
    .agg(units_sold=("transaction_qty", "sum"),
         total_revenue=("revenue", "sum"),
         transactions=("transaction_id", "nunique"))
)
ptype["revenue_share_within_category_pct"] = (
    ptype["total_revenue"] /
    ptype.groupby("product_category")["total_revenue"].transform("sum") * 100
).fillna(0)

st.subheader("Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${total_revenue:,.2f}")
k2.metric("Units Sold", f"{total_units:,.0f}")
k3.metric("Transactions", f"{transaction_count:,.0f}")
k4.metric("Avg. Revenue / Transaction", f"${avg_transaction_revenue:,.2f}")

st.caption(
    f"Showing {len(filtered):,} transaction rows from "
    f"{filtered['store_location'].nunique()} store location(s)."
)

# Product popularity and revenue
st.divider()
st.header("1. Product Popularity Analysis")
left, right = st.columns(2)
top_units = product.nlargest(10, "units_sold").sort_values("units_sold")
bottom_units = product.nsmallest(10, "units_sold").sort_values("units_sold")

with left:
    st.markdown("**Top 10 products by units sold**")
    fig = px.bar(top_units, x="units_sold", y="product_detail", orientation="h",
                 color="product_category", labels={"units_sold": "Units sold", "product_detail": "Product"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("**10 least-selling products by units sold**")
    fig = px.bar(bottom_units, x="units_sold", y="product_detail", orientation="h",
                 color="product_category", labels={"units_sold": "Units sold", "product_detail": "Product"})
    st.plotly_chart(fig, use_container_width=True)

# Revenue contribution
st.divider()
st.header("2. Revenue Contribution Analysis")
left, right = st.columns(2)
top_revenue = product.nlargest(10, "total_revenue").sort_values("total_revenue")
with left:
    st.markdown("**Top 10 products by total revenue**")
    fig = px.bar(top_revenue, x="total_revenue", y="product_detail", orientation="h",
                 color="product_category", labels={"total_revenue": "Revenue", "product_detail": "Product"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("**Revenue share by product category**")
    fig = px.pie(category, names="product_category", values="total_revenue", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("**Product sales rank vs. revenue rank**")
rank_fig = px.scatter(
    product, x="sales_rank", y="revenue_rank", size="total_revenue",
    color="product_category", hover_name="product_detail",
    hover_data={"units_sold": True, "total_revenue": ":.2f", "revenue_share_pct": ":.2f",
                "sales_rank": True, "revenue_rank": True},
    labels={"sales_rank": "Sales volume rank (1 = highest)",
            "revenue_rank": "Revenue rank (1 = highest)"}
)
rank_fig.update_yaxes(autorange="reversed")
st.plotly_chart(rank_fig, use_container_width=True)

# Category and product type performance
st.divider()
st.header("3. Category & Product-Type Performance")
left, right = st.columns(2)
with left:
    st.markdown("**Revenue by product category**")
    fig = px.bar(category.sort_values("total_revenue"), x="total_revenue", y="product_category",
                 orientation="h", text_auto=".2s",
                 labels={"total_revenue": "Revenue", "product_category": "Category"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("**Product-type revenue within each category**")
    fig = px.bar(ptype, x="product_category", y="total_revenue", color="product_type",
                 labels={"total_revenue": "Revenue", "product_category": "Category",
                         "product_type": "Product type"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("**Product-type contribution within category (%)**")
ptype_display = ptype.sort_values(["product_category", "total_revenue"], ascending=[True, False])
st.dataframe(
    ptype_display[["product_category", "product_type", "units_sold",
                   "total_revenue", "revenue_share_within_category_pct"]].rename(columns={
        "product_category": "Category", "product_type": "Product type",
        "units_sold": "Units sold", "total_revenue": "Revenue",
        "revenue_share_within_category_pct": "Revenue share within category (%)"
    }).style.format({"Revenue": "${:,.2f}", "Revenue share within category (%)": "{:.2f}%"}),
    use_container_width=True, hide_index=True
)

# Revenue concentration
st.divider()
st.header("4. Revenue Concentration Across the Menu")
pareto = product.sort_values("total_revenue", ascending=False).copy()
pareto["cumulative_revenue_share_pct"] = pareto["revenue_share_pct"].cumsum()
top_n = min(10, len(pareto))
top_n_share = pareto.head(top_n)["revenue_share_pct"].sum()
c1, c2 = st.columns(2)
c1.metric(f"Revenue share from top {top_n} products", f"{top_n_share:.2f}%")
c2.metric("Number of distinct products", f"{len(product):,}")
fig = px.line(pareto.reset_index(drop=True), x=pareto.reset_index(drop=True).index + 1,
              y="cumulative_revenue_share_pct", markers=True,
              labels={"x": "Products ranked by revenue", "cumulative_revenue_share_pct": "Cumulative revenue share (%)"})
fig.update_yaxes(range=[0, 105])
st.plotly_chart(fig, use_container_width=True)

# Detail table and exports
st.divider()
st.header("5. Product Performance Details")
detail = product.sort_values("total_revenue", ascending=False).copy()
st.dataframe(
    detail[["product_id", "product_category", "product_type", "product_detail",
            "units_sold", "total_revenue", "revenue_share_pct", "sales_rank", "revenue_rank"]].rename(columns={
        "product_id": "Product ID", "product_category": "Category",
        "product_type": "Product type", "product_detail": "Product",
        "units_sold": "Units sold", "total_revenue": "Revenue",
        "revenue_share_pct": "Revenue share (%)", "sales_rank": "Sales rank",
        "revenue_rank": "Revenue rank"
    }).style.format({"Revenue": "${:,.2f}", "Revenue share (%)": "{:.2f}%"}),
    use_container_width=True, hide_index=True
)

csv = detail.to_csv(index=False).encode("utf-8")
st.download_button("Download product analysis (CSV)", data=csv,
                   file_name="product_revenue_analysis.csv", mime="text/csv")

# Data-driven recommendations
st.divider()
st.header("6. Business Insights & Recommendations")
best_seller = product.loc[product["units_sold"].idxmax()]
best_revenue = product.loc[product["total_revenue"].idxmax()]
least_seller = product.loc[product["units_sold"].idxmin()]
top_category = category.iloc[0]
st.markdown(
    f"- **Most popular product:** {best_seller['product_detail']} "
    f"({best_seller['units_sold']:,.0f} units sold). Review its availability and maintain suitable stock.\n"
    f"- **Highest revenue product:** {best_revenue['product_detail']} "
    f"(${best_revenue['total_revenue']:,.2f} revenue). Monitor its sales contribution.\n"
    f"- **Lowest unit-sales product:** {least_seller['product_detail']} "
    f"({least_seller['units_sold']:,.0f} units sold). Review customer demand before deciding whether to promote or retain it.\n"
    f"- **Leading category by revenue:** {top_category['product_category']} "
    f"(${top_category['total_revenue']:,.2f}, {top_category['revenue_share_pct']:.2f}% of revenue)."
)
st.info(
    "Interpretation note: Revenue is calculated as transaction quantity × unit price. "
    "The supplied dataset does not contain product cost, so this dashboard measures revenue "
    "contribution and sales performance, not profit or profitability."
)

with st.expander("Methodology and data validation"):
    st.markdown(
        "- Load the supplied transaction-level Excel dataset.\n"
        "- Check that required columns exist and remove rows with missing key fields.\n"
        "- Keep records with positive quantity and non-negative unit price.\n"
        "- Calculate transaction revenue = transaction quantity × unit price.\n"
        "- Aggregate units sold, revenue and transaction counts by product, product type and category.\n"
        "- Calculate product/category revenue share and compare sales-volume rank with revenue rank.\n"
        "- Recalculate all metrics when dashboard filters change."
    )

st.caption("Project: Product Optimization & Revenue Contribution Analysis for Afficionado Coffee Roasters")
