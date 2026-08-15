from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.db.models import User, QuizAttempt
from app.schemas.schemas import LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


@router.get("/", response_model=List[LeaderboardEntry])
def get_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_admin == False).order_by(User.total_xp.desc()).limit(limit).all()

    leaderboard = []
    for rank, user in enumerate(users, 1):
        quizzes_completed = db.query(func.count(QuizAttempt.id)).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.completed == True,
        ).scalar()

        leaderboard.append(LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            total_xp=user.total_xp,
            level=user.level,
            quizzes_completed=quizzes_completed,
        ))
    return leaderboard
