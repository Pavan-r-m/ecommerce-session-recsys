select
  product_id,
  product_category_name,
  total_sales_value,
  total_orders
from {{ ref('product_performance_mart') }}
order by total_sales_value desc
limit 10;
