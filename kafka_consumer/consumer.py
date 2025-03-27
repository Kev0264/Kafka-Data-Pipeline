import json
import os
from kafka import KafkaConsumer
import psycopg2


def create_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


def setup_database(conn):
    with conn.cursor() as cur:
        # Create tables if they don't exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT PRIMARY KEY,
            customer_id INT,
            product_id INT,
            product_name VARCHAR(100),
            quantity INT,
            price DECIMAL(10, 2),
            total DECIMAL(10, 2),
            order_date TIMESTAMP,
            payment_method VARCHAR(50),
            shipping_address VARCHAR(200)
        );

        CREATE TABLE IF NOT EXISTS daily_sales (
            date DATE PRIMARY KEY,
            total_sales DECIMAL(15, 2),
            order_count INT
        );
        """)
        conn.commit()


def process_message(message, conn):
    # order = json.loads(message.value)
    order = message.value

    with conn.cursor() as cur:
        # Insert raw order
        cur.execute("""
        INSERT INTO orders (
            order_id, customer_id, product_id, product_name,
            quantity, price, total, order_date, payment_method, shipping_address
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING
        """, (
            order['order_id'], order['customer_id'], order['product_id'], order['product_name'],
            order['quantity'], order['price'], order['total'], order['order_date'],
            order['payment_method'], order['shipping_address']
        ))

        # Update daily sales aggregation
        order_date = order['order_date'][:10]  # Extract date part
        cur.execute("""
        INSERT INTO daily_sales (date, total_sales, order_count)
        VALUES (%s, %s, 1)
        ON CONFLICT (date) DO UPDATE
        SET total_sales = daily_sales.total_sales + EXCLUDED.total_sales,
            order_count = daily_sales.order_count + 1
        """, (order_date, order['total']))

        conn.commit()


def main():
    conn = create_db_connection()
    setup_database(conn)

    consumer = KafkaConsumer(
        os.getenv('TOPIC_NAME', 'raw_orders'),
        bootstrap_servers=[os.getenv('KAFKA_BROKER')],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='ecommerce-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    try:
        for message in consumer:
            print(f"Processing order ID: {message.value['order_id']}")
            process_message(message, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
