-- Staging model for orders
select * from {{ ref('orders') }}