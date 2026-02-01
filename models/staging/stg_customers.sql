-- Staging model for customers
select * from {{ ref('customers') }}