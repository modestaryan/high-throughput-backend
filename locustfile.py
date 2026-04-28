from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(0.01, 0.05)

    def on_start(self):
        # 🔐 LOGIN FIRST
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test1@gmail.com",
                "password": "123456"
            }
        )

        data = response.json()
        self.token = data["access_token"]

    @task
    def get_me(self):
        self.client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )