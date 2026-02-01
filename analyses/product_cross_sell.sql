-- Product Cross-Sell: Most common product pairs bought together

with order_products as (
  select order_id, product_id
  from main.stg_order_items
),
pairs as (
  select
    a.product_id as product_id_1,
    b.product_id as product_id_2,
    count(*) as pair_count
  from order_products a
  join order_products b on a.order_id = b.order_id and a.product_id < b.product_id
  group by a.product_id, b.product_id
)
select * from pairs
order by pair_count desc
limit 20;