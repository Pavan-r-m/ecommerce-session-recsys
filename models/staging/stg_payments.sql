-- Staging model for payments
select * from {{ ref('payments') }}