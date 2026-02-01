-- Delivery Performance Trends: On-time vs. delayed deliveries by month

select
  strftime(order_delivered_customer_date, '%Y-%m') as month,
  count(*) as total_deliveries,
  sum(case when order_delivered_customer_date <= order_estimated_delivery_date then 1 else 0 end) as on_time_deliveries,
  sum(case when order_delivered_customer_date > order_estimated_delivery_date then 1 else 0 end) as delayed_deliveries
from main.orders_mart
where order_delivered_customer_date is not null and order_estimated_delivery_date is not null
  and order_status = 'delivered'
group by month
order by month;