from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional, Dict

from .database import get_db, engine, Base
from .models import Habit, HabitLog
from .schemas import (
    HabitCreate, HabitResponse, TrackRequest,
    TrackResponse, StreakResponse
)

app = FastAPI(
    title="Habit Tracker API",
    description="Günlük alışkanlık tracking API'si",
    version="0.1.0"
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def compute_streak(history: Dict[date, bool]) -> tuple[int, Optional[date]]:
    done_dates = sorted([d for d, done in history.items() if done])
    if not done_dates:
        return 0, None

    streak = 0
    current = done_dates[-1]
    while current in history and history[current]:
        streak += 1
        current -= timedelta(days=1)

    return streak, done_dates[-1]


@app.get("/habits", response_model=List[HabitResponse])
def list_habits(db: Session = Depends(get_db)):
    habits = db.query(Habit).all()
    return habits


@app.post("/habits", response_model=HabitResponse, status_code=201)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db)):
    db_habit = Habit(
        name=payload.name,
        description=payload.description,
        goal_days_per_week=payload.goal_days_per_week,
        created_at=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


@app.get("/habits/{habit_id}", response_model=HabitResponse)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.post("/habits/{habit_id}/track", response_model=TrackResponse)
def track_habit(
    habit_id: int,
    payload: TrackRequest,
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    track_date = payload.date or date.today()
    
    existing_log = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.log_date == track_date
    ).first()

    if existing_log:
        existing_log.done = payload.done
    else:
        new_log = HabitLog(
            habit_id=habit_id,
            log_date=track_date,
            done=payload.done
        )
        db.add(new_log)

    db.commit()
    return TrackResponse(habit_id=habit_id, date=track_date, done=payload.done)


@app.get("/habits/{habit_id}/streak", response_model=StreakResponse)
def get_streak(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    streak_days, last_tracked = compute_streak(habit.history)
    return StreakResponse(
        habit_id=habit_id,
        streak_days=streak_days,
        last_tracked=last_tracked
    )


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    db.delete(habit)
    db.commit()

@app.patch("/habits/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    if "name" in payload:
        habit.name = payload["name"]
    if "description" in payload:
        habit.description = payload["description"]
    if "goal_days_per_week" in payload:
        habit.goal_days_per_week = payload["goal_days_per_week"]
    if "category" in payload:
        habit.category = payload["category"]
    
    db.commit()
    db.refresh(habit)
    return habit
