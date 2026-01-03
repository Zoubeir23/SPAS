#!/usr/bin/env python
"""Quick API test for analytics dashboard"""
import requests

BASE_URL = "http://localhost:8000/api"

# Login
login_response = requests.post(
    f"{BASE_URL}/auth/login/",
    json={"email": "admin@isi.edu", "password": "password123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# Test analytics dashboard
print("Testing analytics dashboard...")
response = requests.get(f"{BASE_URL}/analytics/dashboard/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS!")
    import json
    print(json.dumps(response.json(), indent=2)[:500])
else:
    print(f"Error: {response.text}")
