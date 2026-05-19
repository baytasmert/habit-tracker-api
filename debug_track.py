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

# Try to track it
track_response = requests.post(f"{BASE_URL}/habits/{habit_id}/track", json={
    "done": True,
    "duration": 10,
    "notes": "Test notes"
})
print(f"Track habit: {track_response.status_code}")
print(f"Response body: {track_response.text}")
if track_response.status_code != 200:
    try:
        print(f"Error detail: {json.dumps(track_response.json(), indent=2)}")
    except:
        pass
