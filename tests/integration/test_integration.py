def test_create_habit(auth_client):
    # API'ye POST gönder
    response = auth_client.post("/habits", json={
        "name": "Koşu",
        "description": "Günlük koşu"
    })

    # Check 1: status code 201 (created) mi?
    assert response.status_code == 201

    # Check 2: dönen data'da name var mı?
    data = response.json()
    assert data["name"] == "Koşu"
    assert data["id"] is not None


def test_track_habit(auth_client):
    # 1. Önce habit oluştur
    create_response = auth_client.post("/habits", json={
        "name": "Meditasyon",
        "description": "Günlük meditasyon"
    })
    habit_id = create_response.json()["id"]

    # 2. Tracking ekle
    track_response = auth_client.post(f"/habits/{habit_id}/track", json={
        "done": True,
        "duration": 10,
        "notes": "Rahat bir seans"
    })

    # Check 1: status code 200 mi?
    assert track_response.status_code == 200

    # Check 2: dönen data'da done: true var mı?
    track_data = track_response.json()
    assert track_data["done"] is True


def test_get_streak(auth_client):
    # 1. Habit oluştur
    create_response = auth_client.post("/habits", json={
        "name": "Kitap okuma",
        "description": "Her gün 30 dakika"
    })
    habit_id = create_response.json()["id"]

    # 2. 2 gün tracking ekle
    auth_client.post(f"/habits/{habit_id}/track", json={"done": True})
    auth_client.post(f"/habits/{habit_id}/track", json={"done": True})

    # 3. Streak al
    streak_response = auth_client.get(f"/habits/{habit_id}/streak")

    # Check 1: status code 200 mi?
    assert streak_response.status_code == 200

    # Check 2: response valid JSON mi?
    streak_data = streak_response.json()
    assert streak_data is not None


# ===== NEW TESTS FOR HABIT TYPE & TAGS FEATURES =====

def test_create_habit_with_habit_type(auth_client):
    """Test creating habit with different types (daily, weekly, count, time)"""
    # Test 1: Daily habit with goal_days_per_week
    response = auth_client.post("/habits", json={
        "name": "Morning Exercise",
        "description": "30 minutes exercise",
        "habit_type": "daily",
        "goal_days_per_week": 5
    })

    assert response.status_code == 201
    data = response.json()
    assert data["habit_type"] == "daily"
    assert data["goal_days_per_week"] == 5

    # Test 2: Count type with goal_count
    response = auth_client.post("/habits", json={
        "name": "Read Pages",
        "habit_type": "count",
        "goal_count": 30
    })

    assert response.status_code == 201
    data = response.json()
    assert data["habit_type"] == "count"
    assert data["goal_count"] == 30

    # Test 3: Time type with target_duration
    response = auth_client.post("/habits", json={
        "name": "Meditation",
        "habit_type": "time",
        "target_duration": 20
    })

    assert response.status_code == 201
    data = response.json()
    assert data["habit_type"] == "time"
    assert data["target_duration"] == 20


def test_create_negative_habit(auth_client):
    """Test creating negative habits (to avoid)"""
    response = auth_client.post("/habits", json={
        "name": "No Smoking",
        "description": "Quit smoking",
        "is_negative": True
    })

    assert response.status_code == 201
    data = response.json()
    assert data["is_negative"] is True
    assert data["name"] == "No Smoking"


def test_create_habit_with_tags(auth_client):
    """Test creating habit with tags"""
    response = auth_client.post("/habits", json={
        "name": "Sports Training",
        "habit_type": "daily",
        "tags": "spor,sağlık,fitness"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["tags"] == "spor,sağlık,fitness"


def test_track_habit_with_mood_emoji(auth_client):
    """Test tracking habit with mood emoji"""
    # Create habit
    create_response = auth_client.post("/habits", json={
        "name": "Daily Workout",
        "habit_type": "daily"
    })
    habit_id = create_response.json()["id"]

    # Track with mood emoji
    track_response = auth_client.post(f"/habits/{habit_id}/track", json={
        "done": True,
        "duration": 45,
        "mood_emoji": "😊",
        "notes": "Great workout today!"
    })

    assert track_response.status_code == 200
    track_data = track_response.json()
    assert track_data["done"] is True


def test_get_habits_with_tag_filter(auth_client):
    """Test filtering habits by tags"""
    # Create multiple habits with different tags
    auth_client.post("/habits", json={
        "name": "Running",
        "tags": "spor,fitness"
    })

    auth_client.post("/habits", json={
        "name": "Painting",
        "tags": "sanat,creativity"
    })

    auth_client.post("/habits", json={
        "name": "Yoga",
        "tags": "spor,sağlık"
    })

    # Filter by 'spor' tag
    response = auth_client.get("/habits?tag=spor")

    assert response.status_code == 200
    habits = response.json()
    assert len(habits) >= 2
    assert all("spor" in h.get("tags", "") for h in habits if "spor" in h.get("tags", ""))


def test_analytics_by_tags(auth_client):
    """Test analytics endpoint that groups by tags"""
    # Create habit with tags and track it
    create_response = auth_client.post("/habits", json={
        "name": "Reading",
        "habit_type": "daily",
        "tags": "eğlence,kişisel gelişim"
    })
    habit_id = create_response.json()["id"]

    # Track it 3 times (3 successful days)
    auth_client.post(f"/habits/{habit_id}/track", json={"done": True, "duration": 30})
    auth_client.post(f"/habits/{habit_id}/track", json={"done": True, "duration": 30})
    auth_client.post(f"/habits/{habit_id}/track", json={"done": False, "duration": 0})

    # Get analytics
    response = auth_client.get("/analytics/by-tags")

    assert response.status_code == 200
    analytics = response.json()
    assert len(analytics) > 0

    # Find our tags in analytics
    tag_names = [a["tag"] for a in analytics]
    assert "eğlence" in tag_names
    assert "kişisel gelişim" in tag_names

    # Check stats structure
    for tag_data in analytics:
        assert "tag" in tag_data
        assert "habits_count" in tag_data
        assert "total_duration" in tag_data
        assert "success_rate" in tag_data
