import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer


def generate_order():
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99},
        {"id": 2, "name": "Smartphone", "price": 699.99},
        {"id": 3, "name": "Headphones", "price": 149.99},
        {"id": 4, "name": "Tablet", "price": 399.99},
        {"id": 5, "name": "Smartwatch", "price": 249.99},
    ]

    product = random.choice(products)
    quantity = random.randint(1, 5)

    return {
        "order_id": random.randint(1000, 9999),
        "customer_id": random.randint(100, 999),
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "price": product["price"],
        "total": product["price"] * quantity,
        "order_date": datetime.now().isoformat(),
        "payment_method": random.choice(["Credit Card", "PayPal", "Debit Card"]),
        "shipping_address": f"{random.randint(1, 1000)} Main St"
    }


def main():

    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[os.getenv('KAFKA_BROKER')],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            print("Connected to Kafka successfully!")
            topic = os.getenv('TOPIC_NAME', 'raw_orders')

            while True:
                try:
                    order = generate_order()
                    producer.send(topic, value=order)
                    print(f"Sent order: {order['order_id']}")
                    time.sleep(random.uniform(0.5, 2))
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {str(e)}")
                    time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"Connection failed (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)

    # producer = KafkaProducer(
    #     bootstrap_servers=[os.getenv('KAFKA_BROKER')],
    #     value_serializer=lambda x: json.dumps(x).encode('utf-8')
    # )

    # topic = os.getenv('TOPIC_NAME', 'raw_orders')

    # while True:
    #     order = generate_order()
    #     producer.send(topic, value=order)
    #     print(f"Sent order: {order['order_id']}")
    #     time.sleep(random.uniform(0.5, 2))


if __name__ == "__main__":
    import os
    print("Starting data generator with config:")
    print(f"KAFKA_BROKER: {os.getenv('KAFKA_BROKER')}")
    print(f"TOPIC_NAME: {os.getenv('TOPIC_NAME')}")
    main()
