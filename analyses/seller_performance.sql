-- Seller Performance: Top sellers by revenue, order count, and customer satisfaction

with seller_orders as (
  select
    oi.seller_id,
    o.order_id,
    o.order_status,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    oi.price
  from main.stg_order_items oi
  join main.stg_orders o on oi.order_id = o.order_id
),
seller_stats as (
  select
    seller_id,
    count(distinct order_id) as total_orders,
    sum(price) as total_revenue,
    avg(case when order_delivered_customer_date <= order_estimated_delivery_date then 1 else 0 end) as pct_on_time
  from seller_orders
  where order_status = 'delivered'
  group by seller_id
)
select * from seller_stats
order by total_revenue desc
limit 20;