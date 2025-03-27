-- This will be executed when the PostgreSQL container starts
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50)
);

INSERT INTO products (product_id, product_name, price, category)
VALUES
    (1, 'Laptop', 999.99, 'Electronics'),
    (2, 'Smartphone', 699.99, 'Electronics'),
    (3, 'Headphones', 149.99, 'Electronics'),
    (4, 'Tablet', 399.99, 'Electronics'),
    (5, 'Smartwatch', 249.99, 'Electronics')
ON CONFLICT (product_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    join_date DATE
);

-- The orders and daily_sales tables will be created by the consumer