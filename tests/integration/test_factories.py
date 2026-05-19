"""Tests using Factory Boy and Faker for data generation"""
from datetime import datetime, timedelta
from tests.factories import HabitFactory, HabitLogFactory


def test_habit_factory_creates_valid_habit(db):
    habit = HabitFactory()
    db.add(habit)
    db.commit()

    assert habit.id is not None
    assert habit.name is not None
    assert habit.category in ["health", "productivity", "fitness", "learning", "other"]
    assert habit.goal_days_per_week >= 1
    assert habit.goal_days_per_week <= 7
    assert habit.is_active is True


def test_habit_factory_with_custom_values(db):
    habit = HabitFactory(
        name="Yoga",
        description="Morning yoga session",
        category="health"
    )
    db.add(habit)
    db.commit()

    assert habit.name == "Yoga"
    assert habit.description == "Morning yoga session"
    assert habit.category == "health"


def test_habit_log_factory_creates_valid_log(db):
    log = HabitLogFactory()
    db.add(log)
    db.commit()

    assert log.id is not None
    assert log.habit_id is not None
    assert log.log_date is not None
    assert isinstance(log.done, bool)
    assert log.duration is not None
    assert log.mood in range(1, 6) or log.mood is None


def test_multiple_habit_logs_for_streak(db):
    habit = HabitFactory()
    db.add(habit)
    db.commit()

    # Create 5 consecutive daily logs
    today = datetime.now().date()
    for i in range(5):
        log_date = today - timedelta(days=4-i)
        log = HabitLogFactory(habit=habit, log_date=log_date, done=True)
        db.add(log)

    db.commit()

    assert len(habit.logs) == 5
    assert habit.tracked_days == 5


def test_habit_factory_batch_create(db):
    habits = HabitFactory.create_batch(3)
    for habit in habits:
        db.add(habit)
    db.commit()

    assert len(habits) == 3
    assert all(h.id is not None for h in habits)
    assert all(h.is_active for h in habits)


def test_habit_with_various_categories(db):
    categories = ["health", "productivity", "fitness", "learning"]
    for category in categories:
        habit = HabitFactory(category=category)
        db.add(habit)

    db.commit()

    assert all(h.category in categories for h in [
        HabitFactory(category="health"),
        HabitFactory(category="productivity"),
        HabitFactory(category="fitness"),
        HabitFactory(category="learning")
    ])


def test_habit_log_with_mood_tracking(db):
    habit = HabitFactory()
    db.add(habit)
    db.commit()

    # Create logs with different moods
    for mood in range(1, 6):
        log = HabitLogFactory(habit=habit, mood=mood)
        db.add(log)

    db.commit()

    assert len(habit.logs) == 5
    moods = [log.mood for log in habit.logs]
    assert all(m in range(1, 6) for m in moods)
