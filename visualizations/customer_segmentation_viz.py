"""
Customer Segmentation Visualization
Creates interactive visualizations for customer segments
"""

import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Connect to DuckDB (read-only to avoid lock conflicts)
conn = duckdb.connect('dev.duckdb', read_only=True)

# Customer Segmentation Data
segmentation_query = """
with customer_metrics as (
  select
    customer_unique_id,
    customer_city,
    customer_state,
    total_spent,
    total_orders,
    date_diff('day', last_order_date, current_date) as days_since_last_order,
    date_diff('day', first_order_date, last_order_date) as customer_lifetime_days
  from main.customer_lifetime_value_mart
),
segmentation as (
  select
    customer_unique_id,
    customer_city,
    customer_state,
    total_spent,
    total_orders,
    days_since_last_order,
    customer_lifetime_days,
    case
      when total_spent > 1000 and days_since_last_order < 90 then 'High-Value Active'
      when total_spent > 1000 and days_since_last_order >= 90 then 'High-Value At-Risk'
      when total_orders >= 3 and days_since_last_order < 180 then 'Loyal'
      when days_since_last_order > 180 then 'Churned'
      when total_orders = 1 then 'One-Time Buyer'
      else 'Regular'
    end as customer_segment
  from customer_metrics
)
select * from segmentation
"""

df = conn.execute(segmentation_query).df()

# 1. Customer Segment Distribution (Pie Chart)
segment_counts = df['customer_segment'].value_counts()
fig1 = px.pie(
    values=segment_counts.values,
    names=segment_counts.index,
    title='Customer Segment Distribution',
    color_discrete_sequence=px.colors.qualitative.Set3,
    hole=0.4
)
fig1.update_traces(textposition='inside', textinfo='percent+label')
fig1.write_html('visualizations/outputs/customer_segment_pie.html')
print("✓ Created: customer_segment_pie.html")

# 2. Scatter Plot: Total Spent vs Days Since Last Order
fig2 = px.scatter(
    df,
    x='days_since_last_order',
    y='total_spent',
    color='customer_segment',
    size='total_orders',
    hover_data=['customer_state', 'customer_city'],
    title='Customer Segmentation: Spend vs Recency',
    labels={
        'days_since_last_order': 'Days Since Last Order',
        'total_spent': 'Total Spent (R$)',
        'customer_segment': 'Segment'
    },
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig2.update_layout(height=600)
fig2.write_html('visualizations/outputs/customer_scatter.html')
print("✓ Created: customer_scatter.html")

# 3. Box Plot: Spending Distribution by Segment
fig3 = px.box(
    df,
    x='customer_segment',
    y='total_spent',
    color='customer_segment',
    title='Spending Distribution by Customer Segment',
    labels={'total_spent': 'Total Spent (R$)', 'customer_segment': 'Segment'},
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig3.update_layout(showlegend=False, height=600)
fig3.write_html('visualizations/outputs/segment_spending_box.html')
print("✓ Created: segment_spending_box.html")

# 4. Heatmap: Segment Metrics
segment_summary = df.groupby('customer_segment').agg({
    'total_spent': 'mean',
    'total_orders': 'mean',
    'days_since_last_order': 'mean',
    'customer_lifetime_days': 'mean'
}).round(2)

fig4 = go.Figure(data=go.Heatmap(
    z=segment_summary.values.T,
    x=segment_summary.index,
    y=['Avg Spent', 'Avg Orders', 'Avg Days Since Last Order', 'Avg Lifetime Days'],
    colorscale='Blues',
    text=segment_summary.values.T,
    texttemplate='%{text:.1f}',
    textfont={"size": 10}
))
fig4.update_layout(
    title='Customer Segment Metrics Heatmap',
    xaxis_title='Customer Segment',
    yaxis_title='Metric',
    height=500
)
fig4.write_html('visualizations/outputs/segment_metrics_heatmap.html')
print("✓ Created: segment_metrics_heatmap.html")

# 5. Geographic Distribution of Segments
segment_state = df.groupby(['customer_state', 'customer_segment']).size().reset_index(name='count')
fig5 = px.bar(
    segment_state,
    x='customer_state',
    y='count',
    color='customer_segment',
    title='Customer Segments by State',
    labels={'count': 'Number of Customers', 'customer_state': 'State'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig5.update_layout(height=600, xaxis={'categoryorder': 'total descending'})
fig5.write_html('visualizations/outputs/segment_by_state.html')
print("✓ Created: segment_by_state.html")

conn.close()
print("\n✅ All customer segmentation visualizations created successfully!")
