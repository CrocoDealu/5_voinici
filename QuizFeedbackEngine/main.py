from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import QuizSubmission, FeedbackResponse, Quiz, QuizAttempt
from langgraph_workflow import quiz_feedback_graph
from mock_data import MOCK_QUIZ, MOCK_QUIZ_2
from copy import deepcopy
import os

from dotenv import load_dotenv
load_dotenv()  # reads .env into os.environ

app = FastAPI(
    title="Quiz Feedback Service",
    description="LangGraph-powered quiz feedback system with LLM integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Quiz Feedback Service API",
        "version": "1.0.0",
        "endpoints": {
            "POST /feedback": "Submit a quiz for feedback",
            "GET /mock-quiz": "Get mock quiz data",
            "GET /mock-quiz-2": "Get second mock quiz data",
            "GET /health": "Health check"
        },
        "openrouter_configured": os.getenv("OPENROUTER_API_KEY") is not None
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "openrouter_api_configured": os.getenv("OPENROUTER_API_KEY") is not None
    }


@app.get("/mock-quiz", response_model=Quiz)
def get_mock_quiz():
    return MOCK_QUIZ


@app.get("/mock-quiz-2", response_model=Quiz)
def get_mock_quiz_2():
    return MOCK_QUIZ_2


@app.post("/feedback", response_model=FeedbackResponse)
def get_quiz_feedback(submission: QuizSubmission):
    try:
        initial_state = {
            "quiz": submission.quiz,
            "analysis": "",
            "feedback": "",
            "score": 0,
            "total_questions": len(submission.quiz.questions),
            "question_details": [],
            "guardrail_check": ""
        }
        
        result = quiz_feedback_graph.invoke(initial_state)
        
        return FeedbackResponse(
            overall_score=result["score"],
            total_questions=result["total_questions"],
            feedback=result["feedback"],
            question_feedback=result["question_details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz: {str(e)}")


@app.post("/feedback/analyze-only")
def analyze_quiz_only(submission: QuizSubmission):
    try:
        initial_state = {
            "quiz": submission.quiz,
            "analysis": "",
            "feedback": "",
            "score": 0,
            "total_questions": len(submission.quiz.questions),
            "question_details": [],
            "guardrail_check": ""
        }
        
        result = quiz_feedback_graph.invoke(initial_state)
        
        return {
            "score": result["score"],
            "total_questions": result["total_questions"],
            "analysis": result["analysis"],
            "question_details": result["question_details"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing quiz: {str(e)}")


@app.post("/feedback/simple", response_model=FeedbackResponse)
def get_quiz_feedback_simple(attempt: QuizAttempt):
    """Accept a compact submission that references questions by ID and provides user answer indices.

    The server will look up the questions from the mock quizzes and set user_answer_index accordingly.
    """
    try:
        # choose base quiz by title if provided, otherwise default to MOCK_QUIZ
        if attempt.title:
            if attempt.title == MOCK_QUIZ.title:
                base = MOCK_QUIZ
            elif attempt.title == MOCK_QUIZ_2.title:
                base = MOCK_QUIZ_2
            else:
                # unknown title — fall back to default
                base = MOCK_QUIZ
        else:
            base = MOCK_QUIZ

        # deep copy so we don't mutate the original mock data
        quiz_copy: Quiz = deepcopy(base)

        # map question id -> index in quiz_copy.questions
        qmap = {q.id: idx for idx, q in enumerate(quiz_copy.questions)}

        for ans in attempt.answers:
            if ans.question_id in qmap:
                quiz_copy.questions[qmap[ans.question_id]].user_answer_index = ans.user_answer_index

        initial_state = {
            "quiz": quiz_copy,
            "analysis": "",
            "feedback": "",
            "score": 0,
            "total_questions": len(quiz_copy.questions),
            "question_details": [],
            "guardrail_check": ""
        }

        result = quiz_feedback_graph.invoke(initial_state)

        return FeedbackResponse(
            overall_score=result["score"],
            total_questions=result["total_questions"],
            feedback=result["feedback"],
            question_feedback=result["question_details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing simple quiz attempt: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
