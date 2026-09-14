# PROFIT PULSE — ENGIVIZ 2026

An interactive data-storytelling dashboard built from the Superstore e-commerce and sales dataset.

## Story

Profit Pulse investigates three questions:
1. Which product sub-categories generate the strongest profit margins?
2. Which geographic areas contribute the largest losses?
3. How does shipping mode affect sales volume, profit, margin, and delivery time?

A supporting analysis explores the relationship between discount depth and profitability.

## Technology

- Python
- Pandas
- Plotly
- Streamlit

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The application expects `superstore.csv` in the same directory as `app.py`.

## Key dashboard features

- Interactive filters for year, category, region, segment, and shipping mode
- KPI cards for sales, profit, margin, and unique orders
- Sub-category profitability analysis
- State-level profit-loss analysis
- Shipping mode comparison
- Discount vs. profitability analysis
- Interactive Plotly tooltips and charts

## Dataset

Sample Superstore dataset downloaded from the ENGIVIZ/Kaggle-provided dataset.

## Hackathon

ENGIVIZ 2026 — GNA University, Engineers' Day 2026.
