from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List


class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    habit_type: str = "daily"
    is_negative: bool = False
    goal_days_per_week: Optional[int] = 7
    goal_count: Optional[int] = None
    target_duration: Optional[int] = None
    tags: Optional[str] = None


class HabitLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    log_date: date
    done: bool
    duration: Optional[int]
    mood_emoji: Optional[str]
    notes: Optional[str]


class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    category: str
    habit_type: str
    is_negative: bool
    goal_days_per_week: int
    goal_count: Optional[int]
    target_duration: Optional[int]
    tags: Optional[str]
    image_url: Optional[str]
    created_at: date
    tracked_days: int
    logs: Optional[List[HabitLogResponse]] = None


class TrackRequest(BaseModel):
    date: Optional[date] = None
    done: bool = True
    duration: Optional[int] = None
    notes: Optional[str] = None
    mood: Optional[int] = None
    mood_emoji: Optional[str] = None


class TrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    habit_id: int
    date: date
    done: bool
    duration: Optional[int] = None
    mood_emoji: Optional[str] = None


class StreakResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    habit_id: int
    streak_days: int
    last_tracked: Optional[date]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    avatar_url: Optional[str]
