# High-Throughput Distributed Backend Service

A high-performance, production-ready distributed backend system built with **FastAPI**, **PostgreSQL**, **Redis**, **Docker**, and **JWT Authentication with Role-Based Access Control (RBAC)**.

Designed for high request throughput, horizontal worker scaling, distributed rate limiting, idempotent request processing, and cloud deployment on AWS EC2.

---

## 🚀 Key Features

* **⚡ Async Architecture**: Built on FastAPI, `asyncpg`, and `redis.asyncio` for non-blocking I/O and low-latency API performance.
* **🔐 Authentication & RBAC**: JWT-based stateless authentication with Role-Based Access Control (`user`, `manager`, `admin`) and `bcrypt` password hashing.
* **🚦 Redis Distributed Rate Limiting**: Centralized Redis fixed-window rate limiter with `X-RateLimit-*` response headers.
* **🔁 Distributed Idempotency**: Header-driven idempotency engine (`X-Idempotency-Key`) preventing duplicate processing under network retries.
* **🔒 Concurrency Safety**: Row-level pessimistic locking (`SELECT ... FOR UPDATE`) and atomic transaction boundaries for race-condition prevention.
* **🐳 Docker & Docker Compose**: Full containerization setup including FastAPI (`web`), PostgreSQL 16 (`db`), Redis 7 (`redis`), and Locust (`locust`).
* **🧪 Automated Test Suite**: Comprehensive async unit and integration tests using Pytest, `httpx`, and in-memory SQLite fixtures.
* **📈 Load Testing Ready**: Built-in Locust benchmark scenarios simulating concurrent users and distributed master/worker execution.

---

## 🏗️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Core backend runtime |
| **Framework** | FastAPI | High-performance async web framework |
| **Database** | PostgreSQL 16 | Relational database with UUID keys |
| **ORM & Async Driver** | SQLAlchemy 2.0 + asyncpg | Asynchronous ORM database access |
| **Cache & Distributed State** | Redis 7 | Distributed caching, rate limiting, & idempotency |
| **Authentication** | JWT (`python-jose`) + `passlib[bcrypt]` | Token issuance and password security |
| **Containerization** | Docker & Docker Compose | Multi-container orchestration |
| **Load Testing** | Locust | Concurrent user load benchmarking |
| **Testing** | Pytest + `pytest-asyncio` + `httpx` | Automated test suite |

---

## 📂 Project Structure

```text
high-throughput-backend/
├── app/
│   ├── api/
│   │   ├── admin.py           # Admin endpoints (RBAC protected)
│   │   ├── auth.py            # Registration & JWT login endpoints
│   │   ├── deps.py            # Auth & RBAC role dependency factors
│   │   └── user.py            # User profile endpoints (Redis cached)
│   ├── core/
│   │   ├── config.py          # App settings via pydantic-settings
│   │   ├── idempotency.py     # Redis idempotency key interceptor
│   │   ├── rate_limiter.py    # Redis rate limiter dependency
│   │   ├── redis.py           # Async Redis client instance
│   │   └── security.py       # Password hashing & JWT token issuance
│   ├── db/
│   │   ├── base.py            # Declarative Base
│   │   └── session.py         # Async SQLAlchemy engine & session factory
│   ├── models/
│   │   └── user.py            # User SQLAlchemy ORM model
│   ├── schemas/
│   │   └── user.py            # Pydantic schemas (UserCreate, UserResponse, etc.)
│   ├── services/
│   │   ├── auth_service.py    # Registration & login service logic
│   │   └── concurrency_service.py # Pessimistic locking demonstration
│   └── main.py                # FastAPI entrypoint, lifespan, CORS & health check
├── docker/
├── load_tests/
│   └── locustfile.py          # Locust load testing scenarios
├── scripts/
│   └── seed_db.py             # Database initial user/admin seeding script
├── tests/
│   ├── conftest.py            # Pytest async fixtures & SQLite test DB
│   ├── test_auth.py           # Registration & login test suite
│   ├── test_idempotency.py    # Idempotency duplicate request tests
│   └── test_rbac.py           # Role-based access control tests
├── Dockerfile                 # Multi-stage production container build
├── docker-compose.yml         # Compose stack (Web, DB, Redis, Locust)
├── locustfile.py              # Root Locust scenario wrapper
├── makefile                   # CLI targets (run, prod, test, seed, docker-up)
├── pyproject.toml             # Dependencies & project metadata
└── README.md                  # Project documentation
```

---

## ⚙️ Quick Start

### 1️⃣ Clone & Set Up Environment

```bash
git clone https://github.com/modestaryan/high-throughput-backend.git
cd high-throughput-backend

python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/high_throughput_db
JWT_SECRET=supersecretjwtkeyforhighthroughputbackend2026
REDIS_HOST=localhost
REDIS_PORT=6379
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=60
```

---

## 🐳 Docker Deployment (Recommended)

Start the full containerized stack (FastAPI, PostgreSQL 16, Redis 7, Locust) with a single command:

```bash
# Launch container stack in detached mode
make docker-up

# Stop and remove containers & volumes
make docker-down
```

---

## 🛠️ Makefile Commands

| Command | Action |
| :--- | :--- |
| `make run` | Start local development server with auto-reload (`uvicorn app.main:app --reload`) |
| `make prod` | Run production server with 6 multi-process workers |
| `make aws-prod` | Run production server with 8 multi-process workers |
| `make test` | Execute full Pytest automated test suite |
| `make seed` | Seed database with initial admin and user accounts |
| `make docker-up` | Build and start full Docker Compose infrastructure |
| `make docker-down` | Tear down Docker Compose infrastructure |
| `make locust-local` | Launch Locust load testing dashboard targeting local backend |

---

## 🔌 API Documentation & Endpoints

Interactive Swagger UI documentation is available at `http://127.0.0.1:8000/docs`.

### Authentication Endpoints

```http
POST /api/v1/auth/register
Header: [Optional] X-Idempotency-Key: <unique-uuid>
Body: { "email": "user@example.com", "password": "securepassword", "role": "user" }
```

```http
POST /api/v1/auth/login
Body: { "email": "user@example.com", "password": "securepassword" }
Response: { "access_token": "<jwt>", "token_type": "bearer", "user": { ... } }
```

### User Profile Endpoints

```http
GET /api/v1/users/me
Header: Authorization: Bearer <token>
Response: { "id": "<uuid>", "email": "user@example.com", "role": "user" }
```

### Admin Endpoints (RBAC Restricted: `role = admin`)

```http
GET /api/v1/admin/users
Header: Authorization: Bearer <admin-token>
```

```http
PATCH /api/v1/admin/users/{user_id}/role
Header: Authorization: Bearer <admin-token>
Body: { "role": "manager" }
```

```http
GET /api/v1/admin/stats
Header: Authorization: Bearer <admin-token>
```

### Health Check

```http
GET /health
Response: { "status": "healthy", "database": "ok", "redis": "ok" }
```

---

## 🧪 Running Automated Tests

Run the full async Pytest test suite:

```bash
make test
```

---

## 📈 Load Testing with Locust

Launch the Locust web dashboard:

```bash
make locust-local
```

Access the dashboard at `http://localhost:8089` to simulate concurrent virtual users.

---

## 📜 License

Developed for academic and educational purposes.
