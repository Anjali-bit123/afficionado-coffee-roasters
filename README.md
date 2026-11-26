# Product Optimization & Revenue Contribution Analysis for Afficionado Coffee Roasters

## Project overview
This project analyzes transaction-level sales data for Afficionado Coffee Roasters. It identifies popular and low-selling products, measures revenue contribution by product and category, compares sales-volume rank with revenue rank, and evaluates product-type performance.

The project includes an interactive Streamlit dashboard built with Python, Pandas and Plotly.

## Objectives covered
- Identify top-selling and least-selling products.
- Quantify revenue contribution by product and category.
- Measure revenue concentration across the menu.
- Compare product sales-volume rank with revenue rank.
- Analyze revenue share by category (including the categories present in the supplied dataset).
- Analyze product-type contribution within each category.
- Provide data-driven menu and merchandising insights.

## Dataset
`Afficionado Coffee Roasters.xlsx` contains the supplied `Transactions` sheet with 149,116 transaction rows and these fields:

| Column | Description |
|---|---|
| transaction_id | Unique transaction identifier |
| year | Transaction year |
| transaction_time | Transaction time |
| transaction_qty | Quantity purchased |
| store_id | Store identifier |
| store_location | Physical store location |
| product_id | Product identifier |
| unit_price | Price per unit |
| product_category | Broad product group |
| product_type | Product variant/type |
| product_detail | Product details |

## Revenue calculation
`Revenue = transaction_qty × unit_price`

Revenue share is calculated as product/category revenue divided by total revenue in the currently selected data.

**Important limitation:** The supplied dataset does not contain product cost. Therefore, this project analyzes sales and revenue contribution, not gross profit, net profit or product profitability. It does not invent cost values.

## Dashboard features
1. KPI summary: total revenue, units sold, transaction count and average revenue per transaction.
2. Product popularity: top 10 and 10 least-selling products by units sold.
3. Revenue contribution: top 10 products by revenue and category revenue share.
4. Sales rank vs revenue rank comparison.
5. Category and product-type performance.
6. Revenue concentration and cumulative revenue share.
7. Product-level detail table and CSV export.
8. Dynamic business insights and filters for year, category and store location.

## Run locally
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL displayed in the terminal (usually `http://localhost:8501`).

## Suggested GitHub repository description
Interactive Python and Streamlit dashboard for product popularity, revenue contribution, category performance and menu optimization using Afficionado Coffee Roasters transaction data.

## Suggested GitHub topics
`python` `data-analytics` `pandas` `streamlit` `plotly` `data-visualization` `revenue-analysis`

## Project structure
```text
Afficionado_Coffee_Roasters_Project/
├── app.py
├── requirements.txt
├── README.md
└── Afficionado Coffee Roasters.xlsx
```
