from pydantic import BaseModel, Field
from typing import List, Optional


class Answer(BaseModel):
    text: str
    is_correct: bool


class Question(BaseModel):
    """Simplified question representation for submissions: only id and the user's answer index.

    The correct answers are stored separately in `answers_key.json` and looked up by id.
    """
    id: int
    user_answer: Optional[int] = None


class Quiz(BaseModel):
    title: str
    questions: List[Question]


class QuizSubmission(BaseModel):
    quiz: Quiz


class FeedbackResponse(BaseModel):
    overall_score: int
    total_questions: int
    feedback: str
    question_feedback: Optional[List[dict]] = None


class AnswerSubmission(BaseModel):
    question_id: int
    # index of the user's selected answer (0-based). Use null if unanswered.
    user_answer: Optional[int] = None


class QuizAttempt(BaseModel):
        """Compact submission: reference questions by ID and provide the user's answer index.

        Example:
        {
            "title": "Collisions and Momentum",   # optional, used to select the mock quiz
            "answers": [ {"question_id": 1, "user_answer": 2}, ... ]
        }
        """
        title: Optional[str] = None
        answers: List[AnswerSubmission]
