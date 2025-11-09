from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from models import Quiz

class QuizState(TypedDict):
    quiz: Quiz
    analysis: str
    feedback: str
    score: int
    total_questions: int
    question_details: List[dict]
    guardrail_check: str

def analyze_quiz(state: QuizState) -> QuizState:
    quiz = state.get("quiz")
    if not quiz or not quiz.questions:
        state["analysis"] = "Error: no quiz provided or no questions"
        state["score"] = 0
        state["total_questions"] = 0
        state["question_details"] = []
        return state

    correct_count = 0
    question_details: List[dict] = []

    for q in quiz.questions:
        user_idx = getattr(q, "user_answer", None)
        correct_idx = getattr(q, "correct_answer", None)
        is_correct = (
            user_idx is not None and
            correct_idx is not None and
            user_idx == correct_idx
        )
        if is_correct:
            correct_count += 1

        options = getattr(q, "options", getattr(q, "answers", []))

        def opt_text(i):
            try:
                v = options[i]
                return v["text"] if isinstance(v, dict) and "text" in v else str(v)
            except Exception:
                return None

        question_details.append({
            "question_id": q.id,
            "question_text": getattr(q, "text", ""),
            "user_answer_index": user_idx,
            "user_answer_text": opt_text(user_idx) if isinstance(user_idx, int) else None,
            "correct_answer_index": correct_idx,
            "correct_answer_text": opt_text(correct_idx) if isinstance(correct_idx, int) else None,
            "is_correct": is_correct,
        })

    analysis = (
        f"Quiz: {quiz.title}\n"
        f"Total Questions: {len(quiz.questions)}\n"
        f"Correct Answers: {correct_count}\n"
        f"Score: {correct_count}/{len(quiz.questions)}\n"
    )

    state.update({
        "analysis": analysis,
        "score": correct_count,
        "total_questions": len(quiz.questions),
        "question_details": question_details
    })
    return state

def generate_feedback(state: QuizState) -> QuizState:
    total = state.get("total_questions", 0)
    score = state.get("score", 0)
    if total == 0:
        state["feedback"] = "No questions to provide feedback on."
        return state

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
        state["feedback"] = (
            f"Excellent — all {total} answers are correct!"
            if score == total else f"Score: {score}/{total}. Keep practicing to improve!"
        )
        return state
    print(api_key)

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model="meta-llama/llama-3.2-3b-instruct:free",
        temperature=0.2,
        top_p=0.9,
    )

    system_prompt = (
        "You are an expert instructor. Provide professional, objective feedback on a quiz attempt. "
        "Emphasize concepts and reasoning. Structure output:\n"
        "1) Summary (1 sentence)\n"
        "2) Missed concepts (bullets: per-question, state the principle that should apply)\n"
        "3) What to review next (bullets: topics, laws, or formulas)\n"
        "Keep it about 150-200 words. If data for a question is missing, note 'insufficient data'."
    )

    lines: List[str] = []
    for q in state.get("question_details", []):
        status = "correct" if q["is_correct"] else "incorrect"
        qtxt = q.get("question_text") or ""
        ua = q.get("user_answer_text") or f"index {q.get('user_answer_index')}"
        ca = q.get("correct_answer_text") or f"index {q.get('correct_answer_index')}"
        lines.append(f"Q{q['question_id']} [{status}]: {qtxt} | chosen: {ua} | correct: {ca}")

    user_prompt = f"{state.get('analysis','').strip()}\nPer-question:\n" + "\n".join(lines)

    try:
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        response = llm.invoke(messages)
        state["feedback"] = str(response.content)
        print("response:", response.content)
    except Exception as exc:
        # Print available results (analysis & per-question details) for debugging
        # without exposing secrets. Provide a short, friendly generic message to the user
        # that also includes the number of correct answers.
        print("LLM invocation failed:", exc)
        print("Analysis:\n", state.get("analysis", "<no analysis>"))
        print("Question details:\n", state.get("question_details", []))
        # Include score/total in the friendly message for the user
        total = state.get("total_questions", 0)
        score = state.get("score", 0)
        # Friendly user-facing message (non-judgmental) and include results
        state["feedback"] = f"We received your results but our AI is shy at the moment — here are your results: {score}/{total} correct."
    return state

def apply_guardrails(state: QuizState) -> QuizState:
    harmful = ["stupid", "dumb", "idiot", "failure", "give up"]
    negative = ["you failed", "you're bad"]
    text = (state.get("analysis", "") + " " + state.get("feedback", "")).lower()
    violations = [p for p in harmful + negative if p in text]
    if violations:
        state["guardrail_check"] = "BLOCKED"
        state["feedback"] = "Feedback blocked for safety reasons."
    else:
        state["guardrail_check"] = "APPROVED"
    return state

def create_quiz_feedback_workflow():
    workflow = StateGraph(QuizState)
    workflow.add_node("analyze", analyze_quiz)
    workflow.add_node("generate_feedback", generate_feedback)
    workflow.add_node("guardrails", apply_guardrails)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "generate_feedback")
    workflow.add_edge("generate_feedback", "guardrails")
    workflow.add_edge("guardrails", END)
    return workflow.compile()

quiz_feedback_graph = create_quiz_feedback_workflow()
