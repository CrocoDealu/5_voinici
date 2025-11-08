from pydantic import BaseModel, Field
from typing import List, Optional


class Answer(BaseModel):
    text: str
    is_correct: bool


class Question(BaseModel):
    id: int
    question_text: str
    answers: List[Answer] = Field(..., min_length=4, max_length=4)
    user_answer_index: Optional[int] = None


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
    user_answer_index: Optional[int] = None


class QuizAttempt(BaseModel):
    """Simplified submission: reference questions by ID and provide user's answer index.

    Example:
    {
      "title": "Collisions and Momentum",       # optional, used to pick which mock quiz
      "answers": [ {"question_id": 1, "user_answer_index": 2}, ... ]
    }
    """
    title: Optional[str] = None
    answers: List[AnswerSubmission]
