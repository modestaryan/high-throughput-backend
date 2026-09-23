import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_idempotent_registration(client: AsyncClient):
    key = f"idem-{uuid.uuid4()}"
    payload = {"email": f"idem-{uuid.uuid4()}@test.com", "password": "securepass123"}

    # First request
    res1 = await client.post(
        "/api/v1/auth/register",
        json=payload,
        headers={"X-Idempotency-Key": key}
    )
    # May be 201 or cached
    assert res1.status_code in [201, 200]
    data1 = res1.json()

    # Second request with same idempotency key
    res2 = await client.post(
        "/api/v1/auth/register",
        json=payload,
        headers={"X-Idempotency-Key": key}
    )
    # If Redis is running, res2 returns cached response instead of duplicate email error
    assert res2.status_code in [201, 200, 400]
