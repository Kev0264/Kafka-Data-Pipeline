# Use official Python image
FROM python:3.9-slim

# Set wroking directory
WORKDIR /app

# Install system dependencies (required for psycopg2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Wait for postgres to start
COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# Copy the application code
COPY consumer.py .

# Run the consumer
CMD ["./wait-for-it.sh", "postgres:5432", "--", "python", "consumer.py"]
