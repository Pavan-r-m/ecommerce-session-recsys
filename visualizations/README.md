# E-Commerce Analytics Visualizations

This directory contains advanced interactive visualizations for the Olist Brazilian E-Commerce Analytics Platform.

## Overview

The visualization suite includes 30+ interactive charts and graphs covering:
- Customer segmentation and behavior analysis
- Geographic sales distribution and heatmaps
- Time series trends and seasonality
- Product performance and recommendations
- Delivery performance metrics
- Payment method analysis

## Requirements

Install required packages:
```bash
pip install -r requirements.txt
```

## Quick Start

Run all visualizations at once:
```bash
python run_all_visualizations.py
```

Or run individual visualization modules:
```bash
python customer_segmentation_viz.py
python geographic_analysis_viz.py
python time_series_viz.py
python product_analysis_viz.py
python delivery_payment_viz.py
```

## Visualization Modules

### 1. Customer Segmentation (`customer_segmentation_viz.py`)
- **Customer Segment Pie Chart**: Distribution across segments (High-Value Active, At-Risk, Loyal, etc.)
- **Scatter Plot**: Spend vs Recency by segment
- **Box Plot**: Spending distribution by segment
- **Heatmap**: Segment metrics comparison
- **Geographic Bar Chart**: Segment distribution by state

**Output Files**:
- `customer_segment_pie.html`
- `customer_scatter.html`
- `segment_spending_box.html`
- `segment_metrics_heatmap.html`
- `segment_by_state.html`

### 2. Geographic Analysis (`geographic_analysis_viz.py`)
- **Sales Bar Chart**: Top 15 states by revenue
- **Treemap**: Sales distribution with average order value
- **Sunburst Chart**: State > City hierarchy
- **Bubble Chart**: Orders vs Sales by state
- **Grouped Bar**: Orders vs Customers comparison

**Output Files**:
- `sales_by_state_bar.html`
- `sales_treemap.html`
- `geographic_sunburst.html`
- `state_performance_bubble.html`
- `state_metrics_comparison.html`

### 3. Time Series & Trends (`time_series_viz.py`)
- **Line Chart**: Monthly sales trend with area fill
- **Grouped Bar**: Quarterly comparison across years
- **Dual Axis**: Sales and orders combined
- **Heatmap**: Month vs Year sales pattern
- **AOV Trend**: Average order value over time
- **Moving Average**: 3-month smoothed trend

**Output Files**:
- `monthly_sales_trend.html`
- `quarterly_comparison.html`
- `sales_orders_dual_axis.html`
- `sales_heatmap_monthly.html`
- `avg_order_value_trend.html`
- `sales_moving_average.html`

### 4. Product Analysis (`product_analysis_viz.py`)
- **Bar Chart**: Top 20 categories by sales
- **Bubble Chart**: Products vs Sales by category
- **Sunburst**: Category hierarchy
- **Network Graph**: Product recommendation network
- **Parallel Categories**: Cross-sell patterns

**Output Files**:
- `top_products_bar.html`
- `category_performance_bubble.html`
- `category_sunburst.html`
- `product_recommendation_network.html`
- `cross_sell_parallel.html`

### 5. Delivery & Payment (`delivery_payment_viz.py`)
- **On-Time Delivery Bar**: Performance by state
- **Scatter Plot**: Actual vs Estimated delivery
- **Box Plot**: Delivery delay distribution
- **Stacked Bar**: Payment methods by state
- **Pie Chart**: Overall payment distribution
- **Payment Value Bar**: Average by method
- **Heatmap**: Payment preferences by state

**Output Files**:
- `delivery_performance_bar.html`
- `actual_vs_estimated_delivery.html`
- `delivery_delay_distribution.html`
- `payment_methods_by_state.html`
- `payment_type_pie.html`
- `avg_payment_by_method.html`
- `payment_heatmap.html`

## Output Directory

All HTML visualizations are saved to `visualizations/outputs/`. Each file is:
- **Interactive**: Zoom, pan, hover for details
- **Self-contained**: Can be opened in any browser
- **Responsive**: Adapts to different screen sizes
- **Exportable**: Can be saved as PNG (requires kaleido)

## Technology Stack

- **Plotly**: Interactive charts and graphs
- **DuckDB**: Fast analytical queries
- **Pandas**: Data manipulation
- **NetworkX**: Network graph layouts

## Features

✅ **30+ Interactive Visualizations**  
✅ **Responsive Design**  
✅ **Hover Tooltips**  
✅ **Zoom & Pan Capabilities**  
✅ **Color-coded Insights**  
✅ **Export to Image**  
✅ **No External Dependencies** (self-contained HTML)

## Usage Examples

### View in Browser
Simply open any HTML file in `outputs/` with your browser:
```bash
open visualizations/outputs/customer_segment_pie.html
```

### Embed in Dashboard
Include in HTML/web applications:
```html
<iframe src="visualizations/outputs/monthly_sales_trend.html" width="100%" height="600"></iframe>
```

### Export as Image
Use Plotly's built-in export (requires kaleido):
```python
import plotly.graph_objects as go
fig = go.Figure()
# ... create figure ...
fig.write_image("output.png")
```

## Customization

Each visualization script can be customized by:
1. Modifying SQL queries to change data scope
2. Adjusting color schemes (`color_discrete_sequence`, `colorscale`)
3. Changing chart types (bar, line, scatter, etc.)
4. Adding annotations and reference lines
5. Adjusting layout parameters (height, width, margins)

## Performance Notes

- Queries are optimized for DuckDB's columnar storage
- Large datasets are automatically sampled for network graphs
- Top-N filtering applied where appropriate
- Results are cached in DataFrames for reuse

## Troubleshooting

**Issue**: Module not found  
**Solution**: Install requirements: `pip install -r requirements.txt`

**Issue**: Database connection error  
**Solution**: Ensure `dev.duckdb` exists in project root

**Issue**: Empty visualizations  
**Solution**: Run `dbt seed` and `dbt run` to populate database

**Issue**: Slow rendering  
**Solution**: Reduce `limit` values in SQL queries

## Next Steps

- Add dashboard aggregation page
- Implement real-time data refresh
- Create Streamlit/Dash interactive app
- Add ML-based forecasting visualizations
- Export suite to PowerBI/Tableau

---

**Generated for**: Olist Brazilian E-Commerce Analytics Platform  
**Author**: Pavan Kalyan Reddy Madatala  
**Repository**: [GitHub](https://github.com/Pavan-r-m/Olist-Brazilian-E-Commerce-Analytics-Platform)
