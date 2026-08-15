from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.db.models import (
    Quiz, QuizQuestion, QuizAttempt, AttemptResponse,
    Question, Answer, User
)
from app.core.auth import get_current_user, get_admin_user
from app.schemas.schemas import QuizCreate, QuizOut, SubmitQuiz, QuizAttemptOut, QuestionOut

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])


@router.get("/", response_model=List[QuizOut])
def list_quizzes(subject_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Quiz).filter(Quiz.is_published == True)
    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)
    quizzes = query.options(joinedload(Quiz.subject)).all()

    result = []
    for quiz in quizzes:
        quiz_dict = QuizOut.model_validate(quiz)
        quiz_dict.questions = [
            QuestionOut.model_validate(qq.question)
            for qq in sorted(quiz.quiz_questions, key=lambda x: x.order)
        ]
        result.append(quiz_dict)
    return result


@router.post("/", response_model=QuizOut, status_code=201)
def create_quiz(data: QuizCreate, db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    quiz = Quiz(
        subject_id=data.subject_id,
        title=data.title,
        description=data.description,
        time_limit_seconds=data.time_limit_seconds,
    )
    db.add(quiz)
    db.flush()

    total_points = 0
    for i, qid in enumerate(data.question_ids):
        question = db.query(Question).filter(Question.id == qid).first()
        if not question:
            raise HTTPException(status_code=400, detail=f"Question {qid} not found")
        total_points += question.points
        qq = QuizQuestion(quiz_id=quiz.id, question_id=qid, order=i)
        db.add(qq)

    quiz.total_points = total_points
    quiz.is_published = True
    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).options(joinedload(Quiz.subject)).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz_out = QuizOut.model_validate(quiz)
    quiz_out.questions = [
        QuestionOut.model_validate(qq.question)
        for qq in sorted(quiz.quiz_questions, key=lambda x: x.order)
    ]
    return quiz_out


@router.post("/{quiz_id}/start", response_model=QuizAttemptOut)
def start_quiz(quiz_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempt = QuizAttempt(
        user_id=user.id,
        quiz_id=quiz_id,
        total_points=quiz.total_points,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.post("/{quiz_id}/submit/{attempt_id}", response_model=QuizAttemptOut)
def submit_quiz(
    quiz_id: int,
    attempt_id: int,
    data: SubmitQuiz,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == user.id,
        QuizAttempt.quiz_id == quiz_id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.completed:
        raise HTTPException(status_code=400, detail="Quiz already submitted")

    score = 0
    for resp in data.responses:
        question = db.query(Question).filter(Question.id == resp.question_id).first()
        if not question:
            continue

        is_correct = False
        points_earned = 0

        if resp.answer_id:
            answer = db.query(Answer).filter(
                Answer.id == resp.answer_id,
                Answer.question_id == resp.question_id,
            ).first()
            if answer and answer.is_correct:
                is_correct = True
                points_earned = question.points
        elif resp.text_answer:
            correct_answer = db.query(Answer).filter(
                Answer.question_id == resp.question_id,
                Answer.is_correct == True,
            ).first()
            if correct_answer and resp.text_answer.strip().lower() == correct_answer.text.strip().lower():
                is_correct = True
                points_earned = question.points

        score += points_earned
        attempt_resp = AttemptResponse(
            attempt_id=attempt.id,
            question_id=resp.question_id,
            answer_id=resp.answer_id,
            text_answer=resp.text_answer,
            is_correct=is_correct,
            points_earned=points_earned,
        )
        db.add(attempt_resp)

    # Calculate XP (bonus for high scores)
    xp_earned = score
    percentage = (score / attempt.total_points * 100) if attempt.total_points > 0 else 0
    if percentage >= 90:
        xp_earned = int(xp_earned * 1.5)
    elif percentage >= 70:
        xp_earned = int(xp_earned * 1.2)

    attempt.score = score
    attempt.xp_earned = xp_earned
    attempt.completed = True
    attempt.completed_at = datetime.utcnow()
    attempt.time_taken_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())

    # Update user XP and level
    user.total_xp += xp_earned
    user.level = (user.total_xp // 100) + 1  # Level up every 100 XP

    db.commit()
    db.refresh(attempt)
    return attempt
