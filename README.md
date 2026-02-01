

# Brazilian E-Commerce Analytics with dbt & DuckDB

## 📊 [Open the Interactive Dashboard](https://pavan-r-m.github.io/Olist-Brazilian-E-Commerce-Analytics-Platform/)

This project analyzes the Olist Brazilian E-Commerce Public Dataset using dbt and DuckDB. It demonstrates modern analytics engineering best practices, from raw data ingestion to insightful business analysis.

## Project Goals
- Transform raw Olist CSVs into a clean analytics-ready data model
- Build reusable dbt models for orders, customers, products, payments, and more
- Generate actionable business insights (e.g., sales trends, customer behavior, product performance)
- Showcase modular, version-controlled analytics engineering

## Datasets
The following Olist datasets are included in the `seeds/` folder:
- orders.csv
- customers.csv
- order_items.csv
- products.csv
- payments.csv
- sellers.csv
- category_translation.csv

## How to Use
1. Install dependencies and activate your virtual environment
2. Run `dbt seed` to load the CSVs
3. Run `dbt run` to build models
4. Run `dbt test` to validate data
5. Explore insights in the `analyses/` folder
6. Generate visualizations: `python visualizations/run_all_visualizations.py`

## Project Structure
- `models/` – dbt models (SQL transformations)
  - `staging/` – 7 staging models for clean data layer
  - `marts/` – 3 advanced analytics marts (orders, products, customer LTV)
- `analyses/` – 22 SQL analysis scripts for business insights
- `seeds/` – Raw CSV data (7 files, ~450K rows)
- `visualizations/` – 28 interactive Plotly visualizations
  - `outputs/` – Generated HTML charts and dashboard
- `logs/` – dbt logs
- `macros/` – Custom dbt macros

## 📊 Visualizations

This project includes **28 interactive visualizations** covering:

### Customer Segmentation (5 charts)
- Segment distribution (High-Value, At-Risk, Loyal, Churned)
- Spend vs Recency analysis
- Spending patterns by segment
- Geographic distribution

### Geographic Analysis (5 charts)
- Sales heatmaps by state
- City-level performance
- Revenue distribution treemaps
- State comparison metrics

### Time Series & Trends (6 charts)
- Monthly and quarterly sales trends
- Seasonal patterns
- Moving averages
- Average order value evolution

### Product Performance (5 charts)
- Top-selling categories
- Product recommendation networks
- Cross-sell patterns
- Category hierarchy analysis

### Delivery & Payment (7 charts)
- On-time delivery metrics
- Actual vs estimated delivery
- Payment method preferences
- Regional payment patterns


## 🚀 Interactive Dashboard Features (2026 Update)

**View Dashboard**: Open `visualizations/outputs/index.html` in your browser

**Key Features:**
- **Dynamic Real-Time Filters**: Date range, state, and category filters update all metrics, KPIs, forecasts, and seller stats instantly
- **KPI Cards**: MoM/YoY growth, conversion rate, AOV, retention, delivery time
- **Predictive Analytics**: Revenue forecasting with AI-powered projections
- **Customer Cohort Analysis**: Interactive retention heatmap
- **Seller Performance Dashboard**: Top sellers, ratings, fulfillment metrics
- **AI-Driven Recommendations**: Automated insights panel
- **Quick Stats Ticker**: Live metrics banner
- **Dark Mode**: Toggle for night-friendly viewing
- **Sidebar Navigation & Search**: Instantly find and jump to any chart
- **Responsive & Modern UI**: Mobile-friendly, glassmorphism, smooth animations

**Generate Visualizations**:
```bash
cd visualizations
pip install -r requirements.txt
python run_all_visualizations.py
```

## 🔍 Advanced Analytics Included

- Customer Segmentation using RFM analysis
- Product Recommendation Engine (frequently bought together)
- Time-to-Delivery Prediction Analysis
- Seasonal Sales Forecasting
- Geographic Sales Heatmaps
- Payment Method Preferences by Region
- Cohort Analysis & Customer Retention
- Seller Performance Metrics
- Churn Analysis

---


## 🛠️ How to Update Data

1. Change filters at the top of the dashboard (date, state, category)
2. All metrics, KPIs, forecasts, and seller stats update instantly
3. No page reload required—everything is interactive!

---


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
