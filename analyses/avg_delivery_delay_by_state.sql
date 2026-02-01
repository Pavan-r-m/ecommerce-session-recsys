-- Average Delivery Delay by State

select
  c.customer_state,
  avg(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date)) as avg_delivery_delay_days
from {{ ref('orders_mart') }} o
left join {{ ref('stg_customers') }} c on o.customer_id = c.customer_id
where o.order_delivered_customer_date is not null
  and o.order_estimated_delivery_date is not null
  and o.order_status = 'delivered'
group by c.customer_state
order by avg_delivery_delay_days desc;