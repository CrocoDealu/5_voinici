from models import Quiz, Question


# Simple mock quiz: questions contain only ids and no full text/answers.
# The canonical correct answers are stored in `answers_key.json`.
MOCK_QUIZ = Quiz(
    title="Coliziuni și impuls",
    questions=[
        Question(id=1, user_answer=None),
        Question(id=2, user_answer=None),
        Question(id=3, user_answer=None),
        Question(id=4, user_answer=None),
        Question(id=5, user_answer=None),
        Question(id=6, user_answer=None),
        Question(id=7, user_answer=None),
        Question(id=8, user_answer=None),
        Question(id=9, user_answer=None),
        Question(id=10, user_answer=None),
    ]
)


MOCK_QUIZ_2 = MOCK_QUIZ
