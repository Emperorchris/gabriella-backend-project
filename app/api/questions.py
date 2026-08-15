from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import Question, Answer
from app.core.auth import get_admin_user
from app.schemas.schemas import QuestionCreate, QuestionOut

router = APIRouter(prefix="/api/questions", tags=["Questions"])


@router.get("/", response_model=List[QuestionOut])
def list_questions(subject_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Question)
    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    return query.all()


@router.post("/", response_model=QuestionOut, status_code=201)
def create_question(data: QuestionCreate, db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    question = Question(
        subject_id=data.subject_id,
        text=data.text,
        question_type=data.question_type,
        difficulty=data.difficulty,
        points=data.points,
        explanation=data.explanation,
    )
    db.add(question)
    db.flush()

    for ans in data.answers:
        answer = Answer(question_id=question.id, text=ans.text, is_correct=ans.is_correct)
        db.add(answer)

    db.commit()
    db.refresh(question)
    return question


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
