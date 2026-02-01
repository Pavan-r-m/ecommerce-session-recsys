-- RFM Segmentation: Recency, Frequency, Monetary value for each customer

with orders as (
  select customer_unique_id, order_purchase_timestamp, order_id
  from main.orders_mart
),
payments as (
  select order_id, total_payment
  from main.orders_mart
),
rfm as (
  select
    o.customer_unique_id,
    max(o.order_purchase_timestamp) as last_order_date,
    count(distinct o.order_id) as frequency,
    sum(p.total_payment) as monetary
  from orders o
  left join payments p on o.order_id = p.order_id
  group by o.customer_unique_id
)
select
  customer_unique_id,
  julianday('now') - julianday(last_order_date) as recency_days,
  frequency,
  monetary
from rfm
order by monetary desc;