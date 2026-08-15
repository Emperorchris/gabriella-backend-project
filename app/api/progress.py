from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import User, QuizAttempt, AttemptResponse, Quiz, Subject
from app.core.auth import get_current_user
from app.schemas.schemas import UserProgress, QuizAttemptOut, UserAchievementOut, AchievementOut

router = APIRouter(prefix="/api/progress", tags=["Progress"])


@router.get("/", response_model=UserProgress)
def get_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Total quizzes taken
    total_quizzes = db.query(func.count(QuizAttempt.id)).filter(
        QuizAttempt.user_id == user.id,
        QuizAttempt.completed == True,
    ).scalar()

    # Total answers
    total_answers = db.query(func.count(AttemptResponse.id)).join(QuizAttempt).filter(
        QuizAttempt.user_id == user.id,
    ).scalar()

    total_correct = db.query(func.count(AttemptResponse.id)).join(QuizAttempt).filter(
        QuizAttempt.user_id == user.id,
        AttemptResponse.is_correct == True,
    ).scalar()

    accuracy = (total_correct / total_answers * 100) if total_answers > 0 else 0.0

    # XP to next level
    xp_to_next = ((user.level) * 100) - user.total_xp

    # Recent attempts
    recent = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user.id,
        QuizAttempt.completed == True,
    ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()

    # Subject performance
    subject_perf = {}
    subjects = db.query(Subject).all()
    for subject in subjects:
        attempts = db.query(QuizAttempt).join(Quiz).filter(
            Quiz.subject_id == subject.id,
            QuizAttempt.user_id == user.id,
            QuizAttempt.completed == True,
        ).all()
        if attempts:
            avg_score = sum(a.score for a in attempts) / len(attempts)
            avg_total = sum(a.total_points for a in attempts) / len(attempts)
            subject_perf[subject.name] = {
                "attempts": len(attempts),
                "avg_percentage": round((avg_score / avg_total * 100) if avg_total > 0 else 0, 1),
            }

    # Achievements
    user_achievements = [
        UserAchievementOut(
            achievement=AchievementOut.model_validate(ua.achievement),
            earned_at=ua.earned_at,
        )
        for ua in user.achievements
    ]

    return UserProgress(
        total_quizzes_taken=total_quizzes,
        total_correct_answers=total_correct,
        total_questions_answered=total_answers,
        accuracy_percentage=round(accuracy, 1),
        xp_to_next_level=max(0, xp_to_next),
        recent_attempts=[QuizAttemptOut.model_validate(a) for a in recent],
        achievements=user_achievements,
        subject_performance=subject_perf,
    )
