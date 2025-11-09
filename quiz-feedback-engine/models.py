from typing import List, Optional
from pydantic import BaseModel, Field

class Question(BaseModel):
    id: int = Field(..., description="Question ID")
    text: str = Field(..., description="Text of the question")
    options: List[str] = Field(..., min_items=2, description="List of answer options")
    correct_answer: int = Field(..., ge=0, description="Index of correct option (0-based)")
    user_answer: Optional[int] = Field(None, ge=0, description="User's selected answer index")

class Quiz(BaseModel):
    title: str = Field(..., description="Quiz Title")
    questions: List[Question] = Field(..., description="List of quiz questions")

class QuizSubmission(BaseModel):
    quiz: Quiz

class FeedbackResponse(BaseModel):
    overall_score: int
    total_questions: int
    feedback: str
    question_feedback: Optional[List[dict]] = None
