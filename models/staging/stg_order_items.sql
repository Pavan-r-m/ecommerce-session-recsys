-- Staging model for order_items
select * from {{ ref('order_items') }}