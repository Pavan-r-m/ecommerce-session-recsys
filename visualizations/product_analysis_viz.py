"""
Product Performance and Recommendations Visualization
"""

import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import networkx as nx

# Connect to DuckDB (read-only to avoid lock conflicts)
conn = duckdb.connect('dev.duckdb', read_only=True)

# 1. Top Products Performance
product_query = """
select
  product_id,
  product_category_name,
  total_sales_value,
  total_orders,
  total_freight_value
from main.product_performance_mart
order by total_sales_value desc
limit 20
"""
df_products = conn.execute(product_query).df()

fig1 = px.bar(
    df_products,
    x='product_category_name',
    y='total_sales_value',
    color='total_orders',
    title='Top 20 Product Categories by Sales',
    labels={'total_sales_value': 'Total Sales (R$)', 'product_category_name': 'Category'},
    color_continuous_scale='Blues'
)
fig1.update_layout(height=600, xaxis={'tickangle': -45})
fig1.write_html('visualizations/outputs/top_products_bar.html')
print("✓ Created: top_products_bar.html")

# 2. Category Performance Bubble Chart
category_query = """
select
  product_category_name,
  count(distinct product_id) as product_count,
  sum(total_sales_value) as total_sales,
  sum(total_orders) as total_orders,
  avg(total_sales_value) as avg_sales_per_product
from main.product_performance_mart
where product_category_name is not null
group by product_category_name
having sum(total_sales_value) > 1000
order by total_sales desc
"""
df_categories = conn.execute(category_query).df()

fig2 = px.scatter(
    df_categories,
    x='product_count',
    y='total_sales',
    size='total_orders',
    color='avg_sales_per_product',
    hover_name='product_category_name',
    title='Category Performance: Products vs Sales',
    labels={
        'product_count': 'Number of Products',
        'total_sales': 'Total Sales (R$)',
        'avg_sales_per_product': 'Avg Sales/Product'
    },
    color_continuous_scale='Viridis',
    size_max=50
)
fig2.update_layout(height=600)
fig2.write_html('visualizations/outputs/category_performance_bubble.html')
print("✓ Created: category_performance_bubble.html")

# 3. Sunburst: Category Hierarchy
fig3 = px.sunburst(
    df_categories.head(30),
    path=['product_category_name'],
    values='total_sales',
    color='total_orders',
    title='Top 30 Categories Sales Distribution',
    color_continuous_scale='RdYlGn'
)
fig3.update_layout(height=700)
fig3.write_html('visualizations/outputs/category_sunburst.html')
print("✓ Created: category_sunburst.html")

# 4. Product Recommendations Network
recommendations_query = """
with product_pairs as (
  select
    a.product_id as product_a,
    b.product_id as product_b,
    count(*) as times_bought_together
  from main.stg_order_items a
  join main.stg_order_items b 
    on a.order_id = b.order_id 
    and a.product_id < b.product_id
  group by a.product_id, b.product_id
  having count(*) >= 5
),
product_info as (
  select
    pp.product_a,
    pa.product_category_name as category_a,
    pp.product_b,
    pb.product_category_name as category_b,
    pp.times_bought_together
  from product_pairs pp
  left join main.stg_products pa on pp.product_a = pa.product_id
  left join main.stg_products pb on pp.product_b = pb.product_id
)
select * from product_info
order by times_bought_together desc
limit 50
"""
df_recs = conn.execute(recommendations_query).df()

# Create network visualization data
edge_trace = []
node_x = []
node_y = []
node_text = []

# Simple circular layout for top recommendations
import math
top_products = set(list(df_recs['category_a'].head(20)) + list(df_recs['category_b'].head(20)))
product_list = list(top_products)[:15]  # Limit for readability
n = len(product_list)

for i, product in enumerate(product_list):
    angle = 2 * math.pi * i / n
    node_x.append(math.cos(angle))
    node_y.append(math.sin(angle))
    node_text.append(product if product else 'Unknown')

# Add edges
for _, row in df_recs.head(30).iterrows():
    if row['category_a'] in product_list and row['category_b'] in product_list:
        idx_a = product_list.index(row['category_a'])
        idx_b = product_list.index(row['category_b'])
        edge_trace.append(
            go.Scatter(
                x=[node_x[idx_a], node_x[idx_b]],
                y=[node_y[idx_a], node_y[idx_b]],
                mode='lines',
                line=dict(width=row['times_bought_together']/3, color='lightgray'),
                hoverinfo='none',
                showlegend=False
            )
        )

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    marker=dict(size=20, color='lightblue', line=dict(width=2, color='darkblue')),
    text=node_text,
    textposition='top center',
    hoverinfo='text'
)

fig4 = go.Figure(data=edge_trace + [node_trace])
fig4.update_layout(
    title='Product Recommendation Network (Categories Bought Together)',
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    height=700
)
fig4.write_html('visualizations/outputs/product_recommendation_network.html')
print("✓ Created: product_recommendation_network.html")

# 5. Parallel Categories: Cross-sell Analysis
df_recs_sample = df_recs.head(50).copy()
fig5 = go.Figure(data=[go.Parcats(
    dimensions=[
        {'label': 'Category A', 'values': df_recs_sample['category_a']},
        {'label': 'Category B', 'values': df_recs_sample['category_b']}
    ],
    line={'color': df_recs_sample['times_bought_together'], 
          'colorscale': 'Blues',
          'cmin': df_recs_sample['times_bought_together'].min(),
          'cmax': df_recs_sample['times_bought_together'].max()}
)])
fig5.update_layout(
    title='Product Cross-Sell Patterns (Parallel Categories)',
    height=600
)
fig5.write_html('visualizations/outputs/cross_sell_parallel.html')
print("✓ Created: cross_sell_parallel.html")

conn.close()
print("\n✅ All product analysis visualizations created successfully!")
