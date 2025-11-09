from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import QuizSubmission, FeedbackResponse
from langgraph_workflow import quiz_feedback_graph  # compiled workflow

load_dotenv(dotenv_path=".env")

app = FastAPI(title="Quiz Feedback API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8001",
        "http://localhost:8001",
    ],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["content-type"],
    max_age=86400,
)

@app.post("/feedback", response_model=FeedbackResponse)
def get_quiz_feedback(submission: QuizSubmission):
    quiz = submission.quiz
    if not quiz.questions:
        raise HTTPException(status_code=400, detail="Quiz must contain questions")

    # Initial state for the workflow
    initial_state = {
        "quiz": quiz,
        "analysis": "",
        "feedback": "",
        "score": 0,
        "total_questions": len(quiz.questions),
        "question_details": [],
        "guardrail_check": "",
    }

    # Run the workflow
    result = quiz_feedback_graph.invoke(initial_state)

    # Return the structured response
    return FeedbackResponse(
        overall_score=result["score"],
        total_questions=result["total_questions"],
        feedback=result["feedback"],
        question_feedback=result["question_details"],
    )

# Quick check
@app.get("/")
def root():
    return {"service": "Quiz Feedback API", "ok": True}

@app.get("/health")
def health():
    return {"status": "ok"}

