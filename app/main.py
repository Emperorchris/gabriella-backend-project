from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.api import auth, subjects, questions, quizzes, leaderboard, progress

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gamified Learning Platform",
    description="A web-based gamified learning and knowledge assessment platform for students",
    version="1.0.0",
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(questions.router)
app.include_router(quizzes.router)
app.include_router(leaderboard.router)
app.include_router(progress.router)


@app.get("/")
def root():
    return {"message": "Gamified Learning Platform API", "docs": "/docs"}
