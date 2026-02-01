-- Average Order Value by State

select
  c.customer_state,
  avg(o.total_items_value) as avg_order_value
from {{ ref('orders_mart') }} o
left join {{ ref('stg_customers') }} c on o.customer_id = c.customer_id
group by c.customer_state
order by avg_order_value desc;