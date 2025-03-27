# Use official PostgreSQL image
FROM postgres:13

# Copy initilization scripts
COPY init.sql /docker-entrypoint-initdb.d/

# Set environment variables (can be overridden in docker-compose)
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=ecommerce
