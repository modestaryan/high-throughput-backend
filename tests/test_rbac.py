import pytest
from httpx import AsyncClient
from app.models.user import User

@pytest.mark.asyncio
async def test_rbac_admin_endpoint_forbidden_for_normal_user(client: AsyncClient, normal_user: User):
    # Login as normal user
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "user123"}
    )
    token = login_res.json()["access_token"]

    # Try accessing admin endpoint
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

@pytest.mark.asyncio
async def test_rbac_admin_endpoint_allowed_for_admin_user(client: AsyncClient, admin_user: User):
    # Login as admin user
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    token = login_res.json()["access_token"]

    # Access admin users list
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert any(u["email"] == "admin@test.com" for u in users)

@pytest.mark.asyncio
async def test_admin_update_user_role(client: AsyncClient, admin_user: User, normal_user: User):
    # Login as admin user
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    token = login_res.json()["access_token"]

    # Promote normal user to manager
    response = await client.patch(
        f"/api/v1/admin/users/{normal_user.id}/role",
        json={"role": "manager"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "manager"
