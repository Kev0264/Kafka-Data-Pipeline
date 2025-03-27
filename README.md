# Real-Time E-Commerce Analytics Pipeline with Kafka

A Dockerized data pipeline demonstrating real-time order processing using Kafka, PostgreSQL, and Python with an auto-updating dashboard.

## Features

- **Real-time data generation**: Simulated e-commerce orders
- **Kafka pipeline**: Reliable message queue with producers/consumers
- **PostgreSQL storage**: Persistent data storage with analytics tables
- **Live dashboard**: Auto-updating visualization of key metrics
- **Dockerized**: Easy local development and deployment

## Architecture

```mermaid
graph LR
    A[Data Generator] -->|Kafka| B[Kafka Broker]
    B -->|Kafka| C[Kafka Consumer]
    C -->|PostgreSQL| D[(Database)]
    D --> E[Live Dashboard]
```

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM allocated to Docker

## Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Kev0264/Kafka-Data-Pipeline.git
   cd kafka-data-pipeline
   ```

2. **Start the services**:

   ```bash
   docker-compose up --build -d
   ```

3. **Access the dashboard**:
   Open http://localhost:5000 in your browser

## Services Overview

| Service        | Port | Description                       |
| -------------- | ---- | --------------------------------- |
| Data Generator | -    | Produces mock order data to Kafka |
| Kafka Broker   | 9092 | Message queue for order data      |
| Zookeeper      | 2181 | Kafka dependency                  |
| PostgreSQL     | 5432 | Persistent data storage           |
| Dashboard      | 5000 | Real-time analytics visualization |

## Key Endpoints

- **Dashboard**: http://localhost:5000
- **Kafka Topics UI**: http://localhost:8000 (if enabled)
- **PostgreSQL**: `psql -h localhost -U postgres -d ecommerce`

## Monitoring the Pipeline

1. **View Kafka messages**:

   ```bash
   docker-compose exec kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic raw_orders \
     --from-beginning
   ```

2. **Check service logs**:
   ```bash
   docker-compose logs -f [service_name]
   ```

## Customization

### Environment Variables

Edit `.env` file to configure:

- `KAFKA_BROKER`: Kafka connection string
- `TOPIC_NAME`: Kafka topic name
- Database credentials

### Generate More Orders

Increase order generation rate by modifying:

```python
# In data_generator/generate_orders.py
time.sleep(random.uniform(0.1, 0.5))  # Faster generation
```

## Troubleshooting

**Issue**: Kafka container won't start

- **Solution**: Increase Docker memory allocation to at least 4GB

**Issue**: Dashboard not updating

- **Solution**: Check browser console for SSE connection errors

**Issue**: PostgreSQL connection refused

- **Solution**: Wait longer for DB initialization (healthcheck)

## Development

### Accessing Containers

```bash
docker-compose exec kafka bash
docker-compose exec postgres psql -U postgres
```

### Running Tests (not yet implemented)

```bash
docker-compose exec kafka-consumer python -m unittest discover
```

## License

MIT License - See [LICENSE](LICENSE) for details
