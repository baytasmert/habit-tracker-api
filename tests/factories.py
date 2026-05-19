import factory
from factory import fuzzy
from faker import Faker
from datetime import date, timedelta
from src.models import Habit, HabitLog

fake = Faker()

CATEGORIES = ["health", "productivity", "fitness", "learning", "other"]


class HabitFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Habit

    name = factory.LazyFunction(lambda: fake.word())
    description = factory.LazyFunction(lambda: fake.sentence())
    category = fuzzy.FuzzyChoice(CATEGORIES)
    goal_days_per_week = fuzzy.FuzzyInteger(1, 7)
    target_duration = fuzzy.FuzzyInteger(15, 120)
    reminder_time = "09:00"
    color = factory.LazyFunction(lambda: fake.hex_color())
    is_active = True
    created_at = factory.LazyFunction(lambda: fake.date_object())


class HabitLogFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = HabitLog

    habit = factory.SubFactory(HabitFactory)
    log_date = factory.LazyFunction(lambda: fake.date_object())
    done = fuzzy.FuzzyChoice([True, False])
    duration = fuzzy.FuzzyInteger(5, 120)
    notes = factory.LazyFunction(lambda: fake.sentence())
    mood = fuzzy.FuzzyInteger(1, 5)
