"""Seed script to populate the database with sample data."""
from app.db.database import SessionLocal, engine, Base
from app.db.models import User, Subject, Question, Answer, Quiz, QuizQuestion, Achievement
from app.core.auth import hash_password

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # Check if already seeded
    if db.query(User).first():
        print("Database already seeded.")
        db.close()
        return

    # ── Create admin user ──────────────────────────────
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        full_name="Admin User",
        is_admin=True,
    )
    db.add(admin)

    # ── Create sample student ──────────────────────────
    student = User(
        username="student1",
        email="student@example.com",
        hashed_password=hash_password("student123"),
        full_name="Jane Student",
    )
    db.add(student)

    # ── Create subjects ────────────────────────────────
    math = Subject(name="Mathematics", description="Algebra, Geometry, Calculus", icon="📐", color="#EF4444")
    science = Subject(name="Science", description="Physics, Chemistry, Biology", icon="🔬", color="#10B981")
    history = Subject(name="History", description="World History and Events", icon="📜", color="#F59E0B")
    english = Subject(name="English", description="Grammar, Literature, Writing", icon="📖", color="#8B5CF6")
    db.add_all([math, science, history, english])
    db.flush()

    # ── Create questions ───────────────────────────────
    questions_data = [
        # Math
        {"subject": math, "text": "What is 15 × 12?", "answers": [
            ("180", True), ("170", False), ("190", False), ("160", False)
        ]},
        {"subject": math, "text": "What is the square root of 144?", "answers": [
            ("10", False), ("11", False), ("12", True), ("14", False)
        ]},
        {"subject": math, "text": "Solve: 2x + 6 = 20. What is x?", "answers": [
            ("5", False), ("7", True), ("8", False), ("6", False)
        ]},
        {"subject": math, "text": "What is the area of a circle with radius 5? (use π ≈ 3.14)", "answers": [
            ("78.5", True), ("31.4", False), ("15.7", False), ("157", False)
        ]},
        {"subject": math, "text": "What is 3⁴?", "answers": [
            ("12", False), ("27", False), ("81", True), ("64", False)
        ]},
        # Science
        {"subject": science, "text": "What is the chemical symbol for water?", "answers": [
            ("H2O", True), ("CO2", False), ("NaCl", False), ("O2", False)
        ]},
        {"subject": science, "text": "What planet is known as the Red Planet?", "answers": [
            ("Venus", False), ("Mars", True), ("Jupiter", False), ("Saturn", False)
        ]},
        {"subject": science, "text": "What is the powerhouse of the cell?", "answers": [
            ("Nucleus", False), ("Ribosome", False), ("Mitochondria", True), ("Golgi Body", False)
        ]},
        {"subject": science, "text": "What gas do plants absorb from the atmosphere?", "answers": [
            ("Oxygen", False), ("Nitrogen", False), ("Carbon Dioxide", True), ("Hydrogen", False)
        ]},
        {"subject": science, "text": "What is Newton's Second Law of Motion?", "answers": [
            ("F = ma", True), ("E = mc²", False), ("V = IR", False), ("PV = nRT", False)
        ]},
        # History
        {"subject": history, "text": "In what year did World War II end?", "answers": [
            ("1943", False), ("1944", False), ("1945", True), ("1946", False)
        ]},
        {"subject": history, "text": "Who was the first President of the United States?", "answers": [
            ("Thomas Jefferson", False), ("George Washington", True), ("Abraham Lincoln", False), ("John Adams", False)
        ]},
        {"subject": history, "text": "What ancient wonder was located in Egypt?", "answers": [
            ("Colosseum", False), ("Great Pyramid of Giza", True), ("Hanging Gardens", False), ("Lighthouse of Alexandria", False)
        ]},
        # English
        {"subject": english, "text": "What is a synonym for 'happy'?", "answers": [
            ("Sad", False), ("Joyful", True), ("Angry", False), ("Tired", False)
        ]},
        {"subject": english, "text": "Which word is a verb?", "answers": [
            ("Beautiful", False), ("Quickly", False), ("Run", True), ("Happiness", False)
        ]},
    ]

    created_questions = []
    for qdata in questions_data:
        q = Question(
            subject_id=qdata["subject"].id,
            text=qdata["text"],
            points=10,
        )
        db.add(q)
        db.flush()
        for ans_text, is_correct in qdata["answers"]:
            db.add(Answer(question_id=q.id, text=ans_text, is_correct=is_correct))
        created_questions.append(q)

    db.flush()

    # ── Create quizzes ─────────────────────────────────
    math_quiz = Quiz(
        subject_id=math.id,
        title="Math Fundamentals",
        description="Test your basic math skills!",
        time_limit_seconds=300,
        total_points=50,
        is_published=True,
    )
    db.add(math_quiz)
    db.flush()
    for i, q in enumerate(created_questions[:5]):
        db.add(QuizQuestion(quiz_id=math_quiz.id, question_id=q.id, order=i))

    science_quiz = Quiz(
        subject_id=science.id,
        title="Science Explorer",
        description="How well do you know science?",
        time_limit_seconds=300,
        total_points=50,
        is_published=True,
    )
    db.add(science_quiz)
    db.flush()
    for i, q in enumerate(created_questions[5:10]):
        db.add(QuizQuestion(quiz_id=science_quiz.id, question_id=q.id, order=i))

    history_quiz = Quiz(
        subject_id=history.id,
        title="History Challenge",
        description="Journey through time!",
        time_limit_seconds=180,
        total_points=30,
        is_published=True,
    )
    db.add(history_quiz)
    db.flush()
    for i, q in enumerate(created_questions[10:13]):
        db.add(QuizQuestion(quiz_id=history_quiz.id, question_id=q.id, order=i))

    english_quiz = Quiz(
        subject_id=english.id,
        title="English Basics",
        description="Test your language skills!",
        time_limit_seconds=120,
        total_points=20,
        is_published=True,
    )
    db.add(english_quiz)
    db.flush()
    for i, q in enumerate(created_questions[13:15]):
        db.add(QuizQuestion(quiz_id=english_quiz.id, question_id=q.id, order=i))

    # ── Create achievements ────────────────────────────
    achievements = [
        Achievement(name="First Steps", description="Complete your first quiz", badge_icon="🎯", quizzes_required=1),
        Achievement(name="Quiz Master", description="Complete 10 quizzes", badge_icon="🏆", quizzes_required=10),
        Achievement(name="Scholar", description="Earn 500 XP", badge_icon="🎓", xp_required=500),
        Achievement(name="Genius", description="Earn 1000 XP", badge_icon="🧠", xp_required=1000),
        Achievement(name="Streak Champion", description="Maintain a 7-day streak", badge_icon="🔥", streak_required=7),
        Achievement(name="Perfect Score", description="Score 100% on any quiz", badge_icon="⭐", quizzes_required=0),
    ]
    db.add_all(achievements)

    db.commit()
    db.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
