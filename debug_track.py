import requests
import json

BASE_URL = "http://localhost:8001"

# Create a habit first
create_response = requests.post(f"{BASE_URL}/habits", json={
    "name": "Test Habit",
    "description": "Test"
})
print(f"Create habit: {create_response.status_code}")
habit_id = create_response.json()["id"]

# Try with form data instead of JSON
track_response = requests.post(
    f"{BASE_URL}/habits/{habit_id}/track",
    data={
        "done": "true",
        "duration": "10",
        "notes": "Test notes"
    }
)
print(f"Track habit (form data): {track_response.status_code}")
print(f"Response body: {track_response.text}")

# Try with JSON
track_response2 = requests.post(
    f"{BASE_URL}/habits/{habit_id}/track",
    json={
        "done": True,
        "duration": 10,
        "notes": "Test notes"
    }
)
print(f"Track habit (JSON): {track_response2.status_code}")
print(f"Response body: {track_response2.text}")
