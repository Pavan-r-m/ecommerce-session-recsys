-- Staging model for products
select * from {{ ref('products') }}