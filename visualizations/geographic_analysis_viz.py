"""
Geographic Analysis Visualization
Creates interactive maps and geographic visualizations
"""

import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Connect to DuckDB (read-only to avoid lock conflicts)
conn = duckdb.connect('dev.duckdb', read_only=True)

# Geographic Sales Data
geo_query = """
with state_sales as (
  select
    c.customer_state,
    c.customer_city,
    count(distinct o.order_id) as total_orders,
    sum(o.total_items_value) as total_sales,
    count(distinct o.customer_id) as unique_customers
  from main.orders_mart o
  join main.stg_customers c on o.customer_id = c.customer_id
  group by c.customer_state, c.customer_city
)
select
  customer_state,
  count(distinct customer_city) as cities_count,
  sum(total_orders) as total_orders,
  sum(total_sales) as total_sales,
  sum(unique_customers) as unique_customers,
  sum(total_sales) / sum(total_orders) as avg_order_value,
  sum(total_sales) / sum(unique_customers) as avg_customer_value
from state_sales
group by customer_state
order by total_sales desc
"""

df = conn.execute(geo_query).df()

# Brazilian state codes mapping for choropleth
state_codes = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

df['state_name'] = df['customer_state'].map(state_codes)

# 1. Sales Heatmap by State (Bar Chart)
fig1 = px.bar(
    df.head(15),
    x='customer_state',
    y='total_sales',
    color='total_sales',
    title='Top 15 States by Total Sales',
    labels={'total_sales': 'Total Sales (R$)', 'customer_state': 'State'},
    color_continuous_scale='Viridis',
    text='total_sales'
)
fig1.update_traces(texttemplate='R$ %{text:.2s}', textposition='outside')
fig1.update_layout(height=600, showlegend=False)
fig1.write_html('visualizations/outputs/sales_by_state_bar.html')
print("✓ Created: sales_by_state_bar.html")

# 2. Treemap: Sales Distribution
fig2 = px.treemap(
    df,
    path=['customer_state'],
    values='total_sales',
    color='avg_order_value',
    title='Sales Distribution by State (Size = Total Sales, Color = Avg Order Value)',
    color_continuous_scale='RdYlGn',
    labels={'total_sales': 'Total Sales', 'avg_order_value': 'Avg Order Value'}
)
fig2.update_layout(height=600)
fig2.write_html('visualizations/outputs/sales_treemap.html')
print("✓ Created: sales_treemap.html")

# 3. Sunburst Chart: Multi-level Geographic View
city_query = """
select
  c.customer_state,
  c.customer_city,
  count(distinct o.order_id) as total_orders,
  sum(o.total_items_value) as total_sales
from main.orders_mart o
join main.stg_customers c on o.customer_id = c.customer_id
group by c.customer_state, c.customer_city
having sum(o.total_items_value) > 1000
order by total_sales desc
limit 100
"""
df_city = conn.execute(city_query).df()

fig3 = px.sunburst(
    df_city,
    path=['customer_state', 'customer_city'],
    values='total_sales',
    color='total_orders',
    title='Geographic Sales Hierarchy (Top 100 Cities)',
    color_continuous_scale='Blues'
)
fig3.update_layout(height=700)
fig3.write_html('visualizations/outputs/geographic_sunburst.html')
print("✓ Created: geographic_sunburst.html")

# 4. Bubble Chart: Orders vs Sales by State
fig4 = px.scatter(
    df,
    x='total_orders',
    y='total_sales',
    size='unique_customers',
    color='avg_customer_value',
    hover_name='customer_state',
    title='State Performance: Orders vs Sales (Bubble Size = Customers)',
    labels={
        'total_orders': 'Total Orders',
        'total_sales': 'Total Sales (R$)',
        'avg_customer_value': 'Avg Customer Value'
    },
    color_continuous_scale='Plasma',
    size_max=60
)
fig4.update_layout(height=600)
fig4.write_html('visualizations/outputs/state_performance_bubble.html')
print("✓ Created: state_performance_bubble.html")

# 5. Stacked Bar: Multiple Metrics by Top States
top_states = df.head(10).copy()
fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=top_states['customer_state'],
    y=top_states['total_orders'],
    name='Total Orders',
    marker_color='lightblue'
))
fig5.add_trace(go.Bar(
    x=top_states['customer_state'],
    y=top_states['unique_customers'],
    name='Unique Customers',
    marker_color='coral'
))
fig5.update_layout(
    title='Top 10 States: Orders vs Customers',
    xaxis_title='State',
    yaxis_title='Count',
    barmode='group',
    height=600
)
fig5.write_html('visualizations/outputs/state_metrics_comparison.html')
print("✓ Created: state_metrics_comparison.html")

conn.close()
print("\n✅ All geographic visualizations created successfully!")
