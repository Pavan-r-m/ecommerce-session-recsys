-- Top Product Categories by Revenue

select
  product_category_name,
  sum(total_sales_value) as total_revenue,
  sum(total_orders) as total_orders
from {{ ref('product_performance_mart') }}
group by product_category_name
order by total_revenue desc
limit 10;