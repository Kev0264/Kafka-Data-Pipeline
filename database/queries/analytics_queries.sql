-- 1. Daily Sales Performance
SELECT 
    date_trunc('day', order_date) AS day,
    SUM(total) AS daily_sales,
    COUNT(*) AS order_count,
    AVG(total) AS avg_order_value
FROM orders
GROUP BY day
ORDER BY day DESC;

-- 2. Product Performance Analysis
SELECT 
    product_id,
    product_name,
    COUNT(*) AS units_sold,
    SUM(total) AS total_revenue,
    SUM(total) / SUM(quantity) AS avg_unit_price,
    SUM(quantity) AS total_quantity
FROM orders
GROUP BY product_id, product_name
ORDER BY total_revenue DESC;

-- 3. Customer Spending Analysis
SELECT 
    customer_id,
    COUNT(*) AS order_count,
    SUM(total) AS total_spent,
    AVG(total) AS avg_order_value,
    MAX(order_date) AS last_order_date
FROM orders
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 50;

-- 4. Hourly Sales Trends
SELECT 
    EXTRACT(HOUR FROM order_date) AS hour_of_day,
    SUM(total) AS total_sales,
    COUNT(*) AS order_count
FROM orders
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- 5. Payment Method Analysis
SELECT 
    payment_method,
    COUNT(*) AS order_count,
    SUM(total) AS total_sales,
    AVG(total) AS avg_order_value
FROM orders
GROUP BY payment_method
ORDER BY total_sales DESC;

-- 6. Customer Cohort Analysis (by month joined)
WITH customer_first_orders AS (
    SELECT 
        customer_id,
        MIN(date_trunc('month', order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
monthly_metrics AS (
    SELECT 
        c.cohort_month,
        date_trunc('month', o.order_date) AS order_month,
        COUNT(DISTINCT o.customer_id) AS customers,
        SUM(o.total) AS revenue
    FROM orders o
    JOIN customer_first_orders c ON o.customer_id = c.customer_id
    GROUP BY c.cohort_month, order_month
)
SELECT 
    cohort_month,
    order_month,
    EXTRACT(MONTH FROM age(order_month, cohort_month)) AS month_number,
    customers,
    revenue
FROM monthly_metrics
ORDER BY cohort_month, order_month;

-- 7. Repeat Customer Rate
WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT 
    COUNT(*) AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_rate_percentage
FROM customer_order_counts;

-- 8. Sales Growth Rate (Month-over-Month)
WITH monthly_sales AS (
    SELECT 
        date_trunc('month', order_date) AS month,
        SUM(total) AS monthly_sales
    FROM orders
    GROUP BY month
)
SELECT 
    current.month,
    current.monthly_sales,
    previous.monthly_sales AS previous_month_sales,
    ROUND(100.0 * (current.monthly_sales - previous.monthly_sales) / previous.monthly_sales, 2) AS growth_rate_percentage
FROM monthly_sales current
LEFT JOIN monthly_sales previous ON current.month = previous.month + interval '1 month'
ORDER BY current.month DESC;

-- 9. Customer Lifetime Value (CLV) Projection
WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(*) AS order_count,
        SUM(total) AS total_spent,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM orders
    GROUP BY customer_id
)
SELECT 
    AVG(total_spent) AS avg_clv,
    AVG(total_spent / NULLIF(EXTRACT(DAY FROM (last_order_date - first_order_date)), 0)) * 365 AS projected_annual_clv
FROM customer_stats
WHERE EXTRACT(DAY FROM (last_order_date - first_order_date)) > 0;

-- 10. Product Pair Analysis (Frequently Bought Together)
WITH order_products AS (
    SELECT 
        o1.order_id,
        o1.product_id AS product1,
        o2.product_id AS product2
    FROM orders o1
    JOIN orders o2 ON o1.order_id = o2.order_id AND o1.product_id < o2.product_id
)
SELECT 
    p1.product_name AS product1_name,
    p2.product_name AS product2_name,
    COUNT(*) AS times_ordered_together
FROM order_products op
JOIN products p1 ON op.product1 = p1.product_id
JOIN products p2 ON op.product2 = p2.product_id
GROUP BY p1.product_name, p2.product_name
ORDER BY times_ordered_together DESC
LIMIT 10;