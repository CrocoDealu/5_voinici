from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from models import QuizSubmission, FeedbackResponse, Quiz, QuizAttempt
from langgraph_workflow import quiz_feedback_graph
from mock_data import MOCK_QUIZ, MOCK_QUIZ_2
from copy import deepcopy
import os

from dotenv import load_dotenv
load_dotenv()  # reads .env into os.environ

app = FastAPI(
    title="Serviciu Feedback Teste",
    description="Sistem de feedback pentru teste bazat pe LangGraph cu integrare LLM",
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
        "message": "API Serviciu Feedback Teste",
        "version": "1.0.0",
        "endpoints": {
            "POST /feedback": "Trimite un test pentru feedback",
            "GET /mock-quiz": "Obține date de test (mock)",
            "GET /mock-quiz-2": "Obține al doilea test (mock)",
            "GET /health": "Verificare stare"
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
def get_quiz_feedback(payload: dict = Body(...)):
    """Accept either the full `QuizSubmission` shape {"quiz": {..}} or the compact shape
    {"title": "...", "answers": [{"question_id": 1, "user_answer": 2}, ...] }.
    If the compact shape is received, we expand it using the mock quiz data.
    """
    try:
        # If the client sent the full submission shape, validate and use it directly
        if "quiz" in payload:
            submission = QuizSubmission.parse_obj(payload)
            quiz_obj = submission.quiz
        else:
            # expect compact attempt shape (title + answers)
            attempt = QuizAttempt.parse_obj(payload)

            # choose base quiz by title if provided, otherwise default to MOCK_QUIZ
            if attempt.title:
                if attempt.title == MOCK_QUIZ.title:
                    base = MOCK_QUIZ
                elif attempt.title == MOCK_QUIZ_2.title:
                    base = MOCK_QUIZ_2
                else:
                    base = MOCK_QUIZ
            else:
                base = MOCK_QUIZ

            # deep copy so we don't mutate the original mock data
            quiz_copy: Quiz = deepcopy(base)

            # map question id -> index in quiz_copy.questions
            qmap = {q.id: idx for idx, q in enumerate(quiz_copy.questions)}

            for ans in attempt.answers:
                if ans.question_id in qmap:
                    quiz_copy.questions[qmap[ans.question_id]].user_answer = ans.user_answer

            quiz_obj = quiz_copy

        initial_state = {
            "quiz": quiz_obj,
            "analysis": "",
            "feedback": "",
            "score": 0,
            "total_questions": len(quiz_obj.questions),
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
        raise HTTPException(status_code=500, detail=f"Eroare la procesarea testului: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Eroare la analizarea testului: {str(e)}")


# /feedback/simple removed — compact requests are accepted by POST /feedback


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
