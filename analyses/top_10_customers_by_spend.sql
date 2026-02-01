-- Top 10 Customers by Total Spend

select
  customer_unique_id,
  customer_city,
  customer_state,
  total_spent,
  total_orders
from {{ ref('customer_lifetime_value_mart') }}
order by total_spent desc
limit 10;
