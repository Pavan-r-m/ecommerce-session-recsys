SELECT
  product_id,
  product_category_name,
  total_sales_value,
  total_orders
FROM main.product_performance_mart
ORDER BY total_sales_value DESC
LIMIT 10;
