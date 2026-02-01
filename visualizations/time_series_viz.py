"""
Time Series and Seasonal Trends Visualization
Creates trend analysis and forecasting visualizations
"""

import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Connect to DuckDB (read-only to avoid lock conflicts)
conn = duckdb.connect('dev.duckdb', read_only=True)

# Seasonal Trends Data
seasonal_query = """
with monthly_sales as (
  select
    strftime(order_purchase_timestamp, '%Y') as year,
    strftime(order_purchase_timestamp, '%m') as month,
    cast(strftime(order_purchase_timestamp, '%m') as integer) as month_num,
    case
      when cast(strftime(order_purchase_timestamp, '%m') as integer) in (1,2,3) then 'Q1'
      when cast(strftime(order_purchase_timestamp, '%m') as integer) in (4,5,6) then 'Q2'
      when cast(strftime(order_purchase_timestamp, '%m') as integer) in (7,8,9) then 'Q3'
      else 'Q4'
    end as quarter,
    count(distinct order_id) as total_orders,
    sum(total_items_value) as total_sales
  from main.orders_mart
  group by year, month, month_num, quarter
)
select
  year,
  quarter,
  month,
  month_num,
  total_orders,
  total_sales,
  total_sales / total_orders as avg_order_value
from monthly_sales
order by year, month_num
"""

df = conn.execute(seasonal_query).df()
df['year_month'] = df['year'] + '-' + df['month']

# 1. Monthly Sales Trend Line
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df['year_month'],
    y=df['total_sales'],
    mode='lines+markers',
    name='Sales',
    line=dict(color='royalblue', width=3),
    marker=dict(size=8),
    fill='tozeroy',
    fillcolor='rgba(65, 105, 225, 0.2)'
))
fig1.update_layout(
    title='Monthly Sales Trend',
    xaxis_title='Month',
    yaxis_title='Total Sales (R$)',
    height=600,
    hovermode='x unified'
)
fig1.write_html('visualizations/outputs/monthly_sales_trend.html')
print("✓ Created: monthly_sales_trend.html")

# 2. Quarterly Comparison (Grouped Bar)
fig2 = px.bar(
    df,
    x='quarter',
    y='total_sales',
    color='year',
    barmode='group',
    title='Quarterly Sales Comparison Across Years',
    labels={'total_sales': 'Total Sales (R$)', 'quarter': 'Quarter'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig2.update_layout(height=600)
fig2.write_html('visualizations/outputs/quarterly_comparison.html')
print("✓ Created: quarterly_comparison.html")

# 3. Dual Axis: Sales vs Orders
fig3 = make_subplots(specs=[[{"secondary_y": True}]])
fig3.add_trace(
    go.Scatter(x=df['year_month'], y=df['total_sales'], name='Total Sales',
               line=dict(color='green', width=2)),
    secondary_y=False
)
fig3.add_trace(
    go.Scatter(x=df['year_month'], y=df['total_orders'], name='Total Orders',
               line=dict(color='orange', width=2)),
    secondary_y=True
)
fig3.update_layout(title='Sales and Orders Trend', height=600)
fig3.update_xaxes(title_text='Month')
fig3.update_yaxes(title_text='Total Sales (R$)', secondary_y=False)
fig3.update_yaxes(title_text='Total Orders', secondary_y=True)
fig3.write_html('visualizations/outputs/sales_orders_dual_axis.html')
print("✓ Created: sales_orders_dual_axis.html")

# 4. Heatmap: Sales by Month and Year
pivot_data = df.pivot_table(values='total_sales', index='month', columns='year', aggfunc='sum')
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig4 = go.Figure(data=go.Heatmap(
    z=pivot_data.values,
    x=pivot_data.columns,
    y=month_names[:len(pivot_data)],
    colorscale='YlOrRd',
    text=np.round(pivot_data.values, 0),
    texttemplate='R$ %{text:.2s}',
    textfont={"size": 10}
))
fig4.update_layout(
    title='Sales Heatmap: Month vs Year',
    xaxis_title='Year',
    yaxis_title='Month',
    height=600
)
fig4.write_html('visualizations/outputs/sales_heatmap_monthly.html')
print("✓ Created: sales_heatmap_monthly.html")

# 5. Average Order Value Trend
fig5 = px.line(
    df,
    x='year_month',
    y='avg_order_value',
    title='Average Order Value Trend Over Time',
    labels={'avg_order_value': 'Avg Order Value (R$)', 'year_month': 'Month'},
    markers=True,
    color_discrete_sequence=['#ff6b6b']
)
fig5.add_hline(
    y=df['avg_order_value'].mean(),
    line_dash="dash",
    annotation_text=f"Average: R$ {df['avg_order_value'].mean():.2f}",
    line_color="gray"
)
fig5.update_layout(height=600)
fig5.write_html('visualizations/outputs/avg_order_value_trend.html')
print("✓ Created: avg_order_value_trend.html")

# 6. Moving Average (3-month)
df['sales_ma3'] = df['total_sales'].rolling(window=3).mean()
fig6 = go.Figure()
fig6.add_trace(go.Scatter(
    x=df['year_month'],
    y=df['total_sales'],
    mode='lines',
    name='Actual Sales',
    line=dict(color='lightblue', width=1),
    opacity=0.5
))
fig6.add_trace(go.Scatter(
    x=df['year_month'],
    y=df['sales_ma3'],
    mode='lines',
    name='3-Month Moving Average',
    line=dict(color='darkblue', width=3)
))
fig6.update_layout(
    title='Sales with 3-Month Moving Average',
    xaxis_title='Month',
    yaxis_title='Total Sales (R$)',
    height=600
)
fig6.write_html('visualizations/outputs/sales_moving_average.html')
print("✓ Created: sales_moving_average.html")

conn.close()
print("\n✅ All time series visualizations created successfully!")
