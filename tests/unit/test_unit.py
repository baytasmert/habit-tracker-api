from datetime import date
from src.main import compute_streak


# TEST 1: Boş history
def test_compute_streak_empty():
    result = compute_streak({})
    assert result == (0, None)


# TEST 2: Bir gün
def test_compute_streak_one_day():
    history = {date(2026, 5, 14): True}
    result = compute_streak(history)
    assert result == (1, date(2026, 5, 14))


# TEST 3: Art arda 3 gün
def test_compute_streak_three_days():
    history = {
        date(2026, 5, 12): True,
        date(2026, 5, 13): True,
        date(2026, 5, 14): True,
    }
    result = compute_streak(history)
    assert result == (3, date(2026, 5, 14))
