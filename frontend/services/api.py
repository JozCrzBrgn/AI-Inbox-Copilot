import os

import requests

API_URL = os.getenv("API_URL", "http://test:8000")


def login(username, password):
    response = requests.post(
        f"{API_URL}/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def analyze(email, token):
    return requests.post(
        f"{API_URL}/v1/analyze",
        json={"email_content": email},
        headers={"Authorization": f"Bearer {token}"}
    )


def get_history(token):
    return requests.get(
        f"{API_URL}/v1/emails",
        headers={"Authorization": f"Bearer {token}"}
    )