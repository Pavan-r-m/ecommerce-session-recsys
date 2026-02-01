-- Monthly Revenue Growth Rate

with monthly_sales as (
  select
    strftime(order_purchase_timestamp, '%Y-%m') as month,
    sum(total_items_value) as total_sales
  from {{ ref('orders_mart') }}
  group by month
)
select
  month,
  total_sales,
  round((total_sales - lag(total_sales) over (order by month)) * 100.0 / nullif(lag(total_sales) over (order by month),0), 2) as revenue_growth_rate_pct
from monthly_sales
order by month;