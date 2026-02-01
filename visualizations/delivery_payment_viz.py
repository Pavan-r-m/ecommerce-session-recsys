"""
Delivery Performance and Payment Analysis Visualizations
"""

import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Connect to DuckDB (read-only to avoid lock conflicts)
conn = duckdb.connect('dev.duckdb', read_only=True)

# 1. Delivery Performance Analysis
delivery_query = """
with delivery_metrics as (
  select
    o.order_id,
    c.customer_state,
    o.order_status,
    date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) as actual_delivery_days,
    date_diff('day', o.order_purchase_timestamp, o.order_estimated_delivery_date) as estimated_delivery_days,
    date_diff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) as delivery_delay_days
  from main.stg_orders o
  join main.stg_customers c on o.customer_id = c.customer_id
  where o.order_delivered_customer_date is not null
    and o.order_estimated_delivery_date is not null
    and o.order_status = 'delivered'
)
select
  customer_state,
  count(*) as total_deliveries,
  avg(actual_delivery_days) as avg_actual_delivery_days,
  avg(estimated_delivery_days) as avg_estimated_delivery_days,
  avg(delivery_delay_days) as avg_delay_days,
  sum(case when delivery_delay_days <= 0 then 1 else 0 end) as on_time_deliveries,
  sum(case when delivery_delay_days <= 0 then 1 else 0 end) * 100.0 / count(*) as on_time_percentage
from delivery_metrics
group by customer_state
order by avg_delay_days desc
"""
df_delivery = conn.execute(delivery_query).df()

fig1 = px.bar(
    df_delivery.head(15),
    x='customer_state',
    y='on_time_percentage',
    color='avg_delay_days',
    title='Top 15 States: On-Time Delivery Performance',
    labels={'on_time_percentage': 'On-Time Delivery %', 'customer_state': 'State'},
    color_continuous_scale='RdYlGn_r',
    text='on_time_percentage'
)
fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig1.update_layout(height=600)
fig1.write_html('visualizations/outputs/delivery_performance_bar.html')
print("✓ Created: delivery_performance_bar.html")

# 2. Actual vs Estimated Delivery Time
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_delivery['customer_state'],
    y=df_delivery['avg_actual_delivery_days'],
    mode='markers',
    name='Actual',
    marker=dict(size=10, color='red')
))
fig2.add_trace(go.Scatter(
    x=df_delivery['customer_state'],
    y=df_delivery['avg_estimated_delivery_days'],
    mode='markers',
    name='Estimated',
    marker=dict(size=10, color='blue')
))
fig2.update_layout(
    title='Actual vs Estimated Delivery Days by State',
    xaxis_title='State',
    yaxis_title='Average Days',
    height=600,
    hovermode='x unified'
)
fig2.write_html('visualizations/outputs/actual_vs_estimated_delivery.html')
print("✓ Created: actual_vs_estimated_delivery.html")

# 3. Delivery Delay Distribution
fig3 = px.box(
    df_delivery,
    y='avg_delay_days',
    title='Distribution of Average Delivery Delays',
    labels={'avg_delay_days': 'Average Delay (days)'},
    color_discrete_sequence=['coral']
)
fig3.update_layout(height=600)
fig3.write_html('visualizations/outputs/delivery_delay_distribution.html')
print("✓ Created: delivery_delay_distribution.html")

# 4. Payment Methods Analysis
payment_query = """
with payment_by_region as (
  select
    c.customer_state,
    p.payment_type,
    count(distinct o.order_id) as order_count,
    sum(p.payment_value) as total_payment_value,
    avg(p.payment_value) as avg_payment_value
  from main.stg_orders o
  join main.stg_customers c on o.customer_id = c.customer_id
  join main.stg_payments p on o.order_id = p.order_id
  group by c.customer_state, p.payment_type
),
state_totals as (
  select
    customer_state,
    sum(order_count) as state_total_orders
  from payment_by_region
  group by customer_state
)
select
  pbr.customer_state,
  pbr.payment_type,
  pbr.order_count,
  pbr.total_payment_value,
  pbr.avg_payment_value,
  pbr.order_count * 100.0 / st.state_total_orders as percentage_of_state_orders
from payment_by_region pbr
join state_totals st on pbr.customer_state = st.customer_state
order by pbr.customer_state, pbr.order_count desc
"""
df_payment = conn.execute(payment_query).df()

# Top 10 states payment distribution
top_states = df_payment.groupby('customer_state')['order_count'].sum().nlargest(10).index
df_payment_top = df_payment[df_payment['customer_state'].isin(top_states)]

fig4 = px.bar(
    df_payment_top,
    x='customer_state',
    y='percentage_of_state_orders',
    color='payment_type',
    title='Payment Method Distribution by Top 10 States',
    labels={'percentage_of_state_orders': 'Percentage of Orders', 'customer_state': 'State'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig4.update_layout(height=600, barmode='stack')
fig4.write_html('visualizations/outputs/payment_methods_by_state.html')
print("✓ Created: payment_methods_by_state.html")

# 5. Payment Type Overall Distribution
payment_overall = df_payment.groupby('payment_type').agg({
    'order_count': 'sum',
    'total_payment_value': 'sum',
    'avg_payment_value': 'mean'
}).reset_index()

fig5 = px.pie(
    payment_overall,
    values='order_count',
    names='payment_type',
    title='Overall Payment Method Distribution',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.4
)
fig5.update_traces(textposition='inside', textinfo='percent+label')
fig5.write_html('visualizations/outputs/payment_type_pie.html')
print("✓ Created: payment_type_pie.html")

# 6. Average Payment Value by Method
fig6 = px.bar(
    payment_overall.sort_values('avg_payment_value', ascending=False),
    x='payment_type',
    y='avg_payment_value',
    color='avg_payment_value',
    title='Average Payment Value by Payment Method',
    labels={'avg_payment_value': 'Avg Payment Value (R$)', 'payment_type': 'Payment Method'},
    color_continuous_scale='Greens',
    text='avg_payment_value'
)
fig6.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
fig6.update_layout(height=600, showlegend=False)
fig6.write_html('visualizations/outputs/avg_payment_by_method.html')
print("✓ Created: avg_payment_by_method.html")

# 7. Heatmap: Payment Methods vs States
pivot_payment = df_payment_top.pivot_table(
    values='percentage_of_state_orders',
    index='payment_type',
    columns='customer_state',
    aggfunc='sum',
    fill_value=0
)

fig7 = go.Figure(data=go.Heatmap(
    z=pivot_payment.values,
    x=pivot_payment.columns,
    y=pivot_payment.index,
    colorscale='Blues',
    text=pivot_payment.values.round(1),
    texttemplate='%{text}%',
    textfont={"size": 10}
))
fig7.update_layout(
    title='Payment Method Preferences Heatmap (Top 10 States)',
    xaxis_title='State',
    yaxis_title='Payment Method',
    height=600
)
fig7.write_html('visualizations/outputs/payment_heatmap.html')
print("✓ Created: payment_heatmap.html")

conn.close()
print("\n✅ All delivery and payment visualizations created successfully!")
