-- Churned Customers: No orders in last 3 months

with last_orders as (
  select customer_unique_id, max(order_purchase_timestamp) as last_order_date
  from {{ ref('orders_mart') }}
  group by customer_unique_id
),
churned as (
  select customer_unique_id, last_order_date
  from last_orders
  where julianday('now') - julianday(last_order_date) > 90
)
select * from churned;