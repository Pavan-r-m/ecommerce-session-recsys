-- Staging model for sellers
select * from {{ ref('sellers') }}