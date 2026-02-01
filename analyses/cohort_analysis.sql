-- Cohort Analysis: Customer retention by signup month

with first_orders as (
  select customer_unique_id, min(strftime(order_purchase_timestamp, '%Y-%m')) as cohort_month
  from main.orders_mart
  group by customer_unique_id
),
orders as (
  select customer_unique_id, strftime(order_purchase_timestamp, '%Y-%m') as order_month
  from main.orders_mart
)
select
  f.cohort_month,
  o.order_month,
  count(distinct o.customer_unique_id) as active_customers
from first_orders f
join orders o on f.customer_unique_id = o.customer_unique_id
where f.cohort_month is not null and o.order_month is not null
  and o.order_month >= f.cohort_month
group by f.cohort_month, o.order_month
order by f.cohort_month, o.order_month;