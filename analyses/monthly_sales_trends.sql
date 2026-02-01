-- Monthly Sales Trends

select
  strftime(order_purchase_timestamp, '%Y-%m') as month,
  sum(total_items_value) as total_sales,
  count(distinct order_id) as total_orders
from {{ ref('orders_mart') }}
group by month
order by month;
