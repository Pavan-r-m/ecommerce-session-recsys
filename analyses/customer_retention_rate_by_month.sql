-- Customer Retention Rate by Month

with first_orders as (
  select customer_unique_id, min(strftime(first_order_date, '%Y-%m')) as first_month
  from {{ ref('customer_lifetime_value_mart') }}
  group by customer_unique_id
),
orders_by_month as (
  select customer_unique_id, strftime(order_purchase_timestamp, '%Y-%m') as month
  from {{ ref('orders_mart') }}
)
select
  month,
  count(distinct customer_unique_id) as active_customers,
  sum(case when month = first_month then 1 else 0 end) as new_customers,
  count(distinct customer_unique_id) - sum(case when month = first_month then 1 else 0 end) as retained_customers,
  round((count(distinct customer_unique_id) - sum(case when month = first_month then 1 else 0 end)) * 1.0 / nullif(count(distinct customer_unique_id),0), 2) as retention_rate
from orders_by_month obm
left join first_orders fo on obm.customer_unique_id = fo.customer_unique_id
group by month, first_month
order by month;