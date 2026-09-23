# Docker Containerization Setup

This folder contains the Docker configuration files for containerizing the **High-Throughput Distributed Backend Service**.

## Container Architecture

- **`web`**: FastAPI application running 4 production Uvicorn workers (`uvicorn app.main:app`).
- **`db`**: PostgreSQL 16 Alpine containerized database.
- **`redis`**: Redis 7 Alpine in-memory key-value store for rate-limiting, idempotency, and caching.
- **`locust`**: Locust load tester container ready for instant benchmarking.

## Usage

From the project root:

```bash
# Start container stack
make docker-up
# or: docker-compose up --build -d

# Stop container stack
make docker-down
# or: docker-compose down -v
```
