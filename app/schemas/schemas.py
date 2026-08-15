from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ───────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    total_xp: int
    level: int
    streak_days: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Subjects ───────────────────────────────────────────
class SubjectCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "📚"
    color: str = "#3B82F6"


class SubjectOut(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    color: str

    class Config:
        from_attributes = True


# ── Answers ────────────────────────────────────────────
class AnswerCreate(BaseModel):
    text: str
    is_correct: bool = False


class AnswerOut(BaseModel):
    id: int
    text: str
    is_correct: bool

    class Config:
        from_attributes = True


# ── Questions ──────────────────────────────────────────
class QuestionCreate(BaseModel):
    subject_id: int
    text: str
    question_type: str = "mcq"
    difficulty: str = "medium"
    points: int = 10
    explanation: str = ""
    answers: List[AnswerCreate] = []


class QuestionOut(BaseModel):
    id: int
    subject_id: int
    text: str
    question_type: str
    difficulty: str
    points: int
    explanation: str
    answers: List[AnswerOut] = []

    class Config:
        from_attributes = True


# ── Quizzes ────────────────────────────────────────────
class QuizCreate(BaseModel):
    subject_id: int
    title: str
    description: str = ""
    time_limit_seconds: int = 600
    question_ids: List[int] = []


class QuizOut(BaseModel):
    id: int
    subject_id: int
    title: str
    description: str
    time_limit_seconds: int
    total_points: int
    is_published: bool
    subject: Optional[SubjectOut] = None
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True


# ── Quiz Attempts ──────────────────────────────────────
class SubmitAnswer(BaseModel):
    question_id: int
    answer_id: Optional[int] = None
    text_answer: Optional[str] = None


class SubmitQuiz(BaseModel):
    responses: List[SubmitAnswer]


class AttemptResponseOut(BaseModel):
    question_id: int
    answer_id: Optional[int] = None
    text_answer: Optional[str] = None
    is_correct: bool
    points_earned: int

    class Config:
        from_attributes = True


class QuizAttemptOut(BaseModel):
    id: int
    quiz_id: int
    score: int
    total_points: int
    xp_earned: int
    time_taken_seconds: int
    completed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    responses: List[AttemptResponseOut] = []

    class Config:
        from_attributes = True


# ── Achievements ───────────────────────────────────────
class AchievementOut(BaseModel):
    id: int
    name: str
    description: str
    badge_icon: str
    xp_required: int
    quizzes_required: int
    streak_required: int

    class Config:
        from_attributes = True


class UserAchievementOut(BaseModel):
    achievement: AchievementOut
    earned_at: datetime

    class Config:
        from_attributes = True


# ── Leaderboard ────────────────────────────────────────
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    total_xp: int
    level: int
    quizzes_completed: int


# ── Dashboard / Progress ──────────────────────────────
class UserProgress(BaseModel):
    total_quizzes_taken: int
    total_correct_answers: int
    total_questions_answered: int
    accuracy_percentage: float
    xp_to_next_level: int
    recent_attempts: List[QuizAttemptOut] = []
    achievements: List[UserAchievementOut] = []
    subject_performance: dict = {}
