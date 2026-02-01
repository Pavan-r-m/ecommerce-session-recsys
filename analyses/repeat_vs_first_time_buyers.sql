-- Repeat vs. First-Time Buyers by Month

with orders as (
  select customer_unique_id, strftime(order_purchase_timestamp, '%Y-%m') as month, order_id
  from {{ ref('orders_mart') }}
),
first_orders as (
  select customer_unique_id, min(month) as first_month
  from orders
  group by customer_unique_id
)
select
  o.month,
  count(distinct case when o.month = f.first_month then o.customer_unique_id end) as first_time_buyers,
  count(distinct case when o.month > f.first_month then o.customer_unique_id end) as repeat_buyers
from orders o
left join first_orders f on o.customer_unique_id = f.customer_unique_id
where o.month is not null
group by o.month
order by o.month;