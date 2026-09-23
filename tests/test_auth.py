import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@test.com", "password": "securepassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "id" in data
    assert data["role"] == "user"

@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient):
    payload = {"email": "duplicate@test.com", "password": "password123"}
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient):
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "loginuser@test.com", "password": "mypassword123"}
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "loginuser@test.com", "password": "mypassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "loginuser@test.com"

@pytest.mark.asyncio
async def test_login_user_invalid_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@test.com", "password": "correctpassword"}
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]
