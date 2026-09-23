import uuid
from locust import HttpUser, task, between

class HighThroughputBackendUser(HttpUser):
    wait_time = between(0.001, 0.01)

    def on_start(self):
        self.email = f"locust_{uuid.uuid4().hex[:8]}@test.com"
        self.password = "password123"

        self.client.post(
            "/api/v1/auth/register",
            json={"email": self.email, "password": self.password}
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": self.email, "password": self.password}
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(5)
    def get_user_profile(self):
        if self.token:
            self.client.get("/api/v1/users/me", headers=self.headers, name="/users/me (Cached)")

    @task(1)
    def health_check(self):
        self.client.get("/health", name="/health")

    @task(1)
    def idempotent_registration_attempt(self):
        idem_key = f"locust-key-{uuid.uuid4()}"
        headers = {"X-Idempotency-Key": idem_key}
        self.client.post(
            "/api/v1/auth/register",
            json={"email": f"idem_{uuid.uuid4().hex[:6]}@test.com", "password": "pass"},
            headers=headers,
            name="/auth/register (Idempotent)"
        )