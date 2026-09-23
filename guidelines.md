# Comprehensive Execution & Testing Guidelines

This document provides a step-by-step operational guide for running, testing, benchmarking, and containerizing the **High-Throughput Distributed Backend Service**.

---

## 📋 Table of Contents

1. [Environment Setup & Configuration](#1-environment-setup--configuration)
2. [Database Seeding](#2-database-seeding)
3. [Running Automated Unit & Integration Tests](#3-running-automated-unit--integration-tests)
4. [Running API Application Servers](#4-running-api-application-servers)
5. [Complete API Endpoints Testing (cURL Inputs & Outputs)](#5-complete-api-endpoints-testing-curl-inputs--outputs)
6. [Testing Advanced Features (Rate Limiting & Idempotency)](#6-testing-advanced-features-rate-limiting--idempotency)
7. [Docker Multi-Container Orchestration](#7-docker-multi-container-orchestration)
8. [Locust Load Testing & Benchmarking](#8-locust-load-testing--benchmarking)

---

## 1. Environment Setup & Configuration

### Step 1: Create Python Virtual Environment & Install Dependencies

```bash
# Navigate to project directory
cd high-throughput-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install editable package with all dependencies
pip install -e .
```

### Step 2: Configure Environment Variables (`.env`)

Create a `.env` file in the project root directory:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/high_throughput_db
JWT_SECRET=supersecretjwtkeyforhighthroughputbackend2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

REDIS_HOST=localhost
REDIS_PORT=6379

RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=60
IDEMPOTENCY_EXPIRE_SECONDS=86400
```

---

## 2. Database Seeding

Populate PostgreSQL with initial admin, manager, and user accounts.

### Command

```bash
make seed
# OR
python scripts/seed_db.py
```

### Expected Output

```text
INFO:scripts.seed_db:Initializing database tables...
INFO:scripts.seed_db:Seeded user: admin@example.com (Role: admin)
INFO:scripts.seed_db:Seeded user: manager@example.com (Role: manager)
INFO:scripts.seed_db:Seeded user: test1@gmail.com (Role: user)
INFO:scripts.seed_db:Database seeding completed successfully.
```

---

## 3. Running Automated Unit & Integration Tests

Execute the full Pytest test suite (covering Auth, RBAC, Idempotency, and Rate Limiting).

### Command

```bash
make test
# OR
PYTHONPATH=. ./venv/bin/pytest -v
```

### Expected Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0
collected 8 items                                                              

tests/test_auth.py::test_register_user_success PASSED                    [ 12%]
tests/test_auth.py::test_register_user_duplicate_email PASSED            [ 25%]
tests/test_auth.py::test_login_user_success PASSED                       [ 37%]
tests/test_auth.py::test_login_user_invalid_password PASSED              [ 50%]
tests/test_idempotency.py::test_idempotent_registration PASSED           [ 62%]
tests/test_rbac.py::test_rbac_admin_endpoint_forbidden_for_normal_user PASSED [ 75%]
tests/test_rbac.py::test_rbac_admin_endpoint_allowed_for_admin_user PASSED [ 87%]
tests/test_rbac.py::test_admin_update_user_role PASSED                   [100%]

============================== 8 passed in 3.55s ===============================
```

---

## 4. Running API Application Servers

### Option A: Development Server (With Auto-Reload)

```bash
make run
```
* **Output**: Server running on `http://127.0.0.1:8000` with Swagger UI at `http://127.0.0.1:8000/docs`.

### Option B: Production Server (6 Workers)

```bash
make prod
```
* **Output**: Launches 6 parallel Uvicorn worker processes listening on `0.0.0.0:8000`.

### Option C: AWS High-Throughput Server (8 Workers)

```bash
make aws-prod
```
* **Output**: Launches 8 parallel Uvicorn worker processes listening on `0.0.0.0:8000`.

---

## 5. Complete API Endpoints Testing (cURL Inputs & Outputs)

### 1️⃣ System Health Check

* **Method & Endpoint**: `GET /health`

#### cURL Input Command
```bash
curl -X GET http://127.0.0.1:8000/health
```

#### Expected Output (HTTP 200 OK)
```json
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok",
  "service": "high-throughput-backend"
}
```

---

### 2️⃣ User Registration

* **Method & Endpoint**: `POST /api/v1/auth/register`

#### cURL Input Command
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "Password123!",
    "role": "user"
  }'
```

#### Expected Output (HTTP 201 Created)
```json
{
  "id": "e4b2a8f1-3c5d-4f67-8e9a-1b2c3d4e5f67",
  "email": "user1@example.com",
  "role": "user"
}
```

#### Error Case: Duplicate Email (HTTP 400 Bad Request)
```json
{
  "detail": "Email already registered"
}
```

---

### 3️⃣ User Login & JWT Token Emission

* **Method & Endpoint**: `POST /api/v1/auth/login`

#### cURL Input Command
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "Password123!"
  }'
```

#### Expected Output (HTTP 200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "e4b2a8f1-3c5d-4f67-8e9a-1b2c3d4e5f67",
    "email": "user1@example.com",
    "role": "user"
  }
}
```

#### Error Case: Invalid Password (HTTP 401 Unauthorized)
```json
{
  "detail": "Invalid email or password credentials"
}
```

---

### 4️⃣ Retrieve Current User Profile (Redis Cached)

* **Method & Endpoint**: `GET /api/v1/users/me`

#### cURL Input Command
```bash
curl -X GET http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### Expected Output (HTTP 200 OK)
```json
{
  "id": "e4b2a8f1-3c5d-4f67-8e9a-1b2c3d4e5f67",
  "email": "user1@example.com",
  "role": "user"
}
```

---

### 5️⃣ Admin: List All Users (RBAC Protected)

* **Method & Endpoint**: `GET /api/v1/admin/users`
* **Requirement**: JWT Token with `role = admin`

#### cURL Input Command (Admin Token)
```bash
# First login as admin@example.com / AdminPassword123! to get ADMIN_TOKEN
curl -X GET http://127.0.0.1:8000/api/v1/admin/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE"
```

#### Expected Output (HTTP 200 OK)
```json
[
  {
    "id": "11111111-2222-3333-4444-555555555555",
    "email": "admin@example.com",
    "role": "admin"
  },
  {
    "id": "e4b2a8f1-3c5d-4f67-8e9a-1b2c3d4e5f67",
    "email": "user1@example.com",
    "role": "user"
  }
]
```

#### Error Case: Non-Admin Access Attempt (HTTP 403 Forbidden)
```json
{
  "detail": "Access denied: Required role (admin), but user has role 'user'"
}
```

---

### 6️⃣ Admin: Update User Role (RBAC Protected)

* **Method & Endpoint**: `PATCH /api/v1/admin/users/{user_id}/role`

#### cURL Input Command
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/admin/users/e4b2a8f1-3c5d-4f67-8e9a-1b2c3d4e5f67/role \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "manager"
  }'
```

#### Expected Output (HTTP 200 OK)
```json
{
  "id": "e4b2a8f1-3c5d-4f67-8e9a-1b2c3d4e5f67",
  "email": "user1@example.com",
  "role": "manager"
}
```

---

### 7️⃣ Admin: System Operational Stats

* **Method & Endpoint**: `GET /api/v1/admin/stats`

#### cURL Input Command
```bash
curl -X GET http://127.0.0.1:8000/api/v1/admin/stats \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE"
```

#### Expected Output (HTTP 200 OK)
```json
{
  "total_users": 3,
  "redis_cached_keys": 5,
  "status": "healthy"
}
```

---

## 6. Testing Advanced Features (Rate Limiting & Idempotency)

### 1️⃣ Testing Idempotent Request Processing (`X-Idempotency-Key`)

Send a registration request with a fixed `X-Idempotency-Key` header:

#### Initial Request (HTTP 201 Created)
```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: test-key-100" \
  -d '{"email": "idem1@example.com", "password": "Password123!"}'
```

#### Duplicate Request (HTTP 201 / HTTP 200 with `X-Cache: Idempotency-Hit`)
```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: test-key-100" \
  -d '{"email": "idem1@example.com", "password": "Password123!"}'
```
* **Result**: Returns the exact cached response payload without creating duplicate DB records or throwing a duplicate email error!

---

### 2️⃣ Testing Rate Limit Thresholds

Send rapid requests to check rate-limiting response headers:

#### cURL Command inspecting Headers
```bash
curl -i -X GET http://127.0.0.1:8000/health
```

#### Expected Response Headers
```http
HTTP/1.1 200 OK
content-type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1774355000
```

#### Exceeded Threshold Response (HTTP 429 Too Many Requests)
```json
{
  "detail": "Rate limit exceeded. Maximum 1000 requests per 60 seconds."
}
```

---

## 7. Docker Multi-Container Orchestration

Launch the full containerized environment containing FastAPI (`web`), PostgreSQL 16 (`db`), Redis 7 (`redis`), and Locust (`locust`).

### Step 1: Start Docker Stack

```bash
make docker-up
# OR
docker-compose up --build -d
```

### Step 2: Verify Running Containers

```bash
docker ps
```

#### Expected Output
```text
CONTAINER ID   IMAGE                COMMAND                  PORTS                    NAMES
a1b2c3d4e5f6   high-backend-web     "uvicorn app.main:..."   0.0.0.0:8000->8000/tcp   backend_app
f6e5d4c3b2a1   postgres:16-alpine   "docker-entrypoint.s…"   0.0.0.0:5432->5432/tcp   postgres_db
1a2b3c4d5e6f   redis:7-alpine       "docker-entrypoint.s…"   0.0.0.0:6379->6379/tcp   redis_cache
9f8e7d6c5b4a   high-backend-web     "locust -f locustfil…"   0.0.0.0:8089->8089/tcp   locust_load_tester
```

### Step 3: Stop Docker Stack

```bash
make docker-down
# OR
docker-compose down -v
```

---

## 8. Locust Load Testing & Benchmarking

### Step 1: Launch Locust Benchmark Dashboard

```bash
make locust-local
```

### Step 2: Access Web UI & Configure Benchmark

Open your browser to: **`http://localhost:8089`**

* **Number of users**: `1000`
* **Spawn rate**: `50`
* **Host**: `http://127.0.0.1:8000`

Click **Start Swarming** to simulate concurrent users hitting authentication, Redis profile cache, and idempotent registration scenarios!
