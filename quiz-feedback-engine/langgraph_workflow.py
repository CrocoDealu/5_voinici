from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from models import Quiz
import json
import pathlib


class QuizState(TypedDict):
    quiz: Quiz
    quizzes: list
    analysis: str
    feedback: str
    score: int
    total_questions: int
    question_details: list
    guardrail_check: str


def analyze_quiz(state: QuizState) -> QuizState:
    # Normalize input: accept either a single `quiz` or a list `quizzes`.
    quizzes = []
    if "quizzes" in state and isinstance(state["quizzes"], list):
        quizzes = state["quizzes"]
    elif "quiz" in state and state["quiz"] is not None:
        quizzes = [state["quiz"]]

    if not quizzes:
        state["analysis"] = "Error: no quiz provided"
        state["score"] = 0
        state["total_questions"] = 0
        state["question_details"] = []
        state["per_quiz_summary"] = []
        return state

    # Load canonical answers from answers_key.json (mapping question_id -> correct answer index)
    answers_file = pathlib.Path(__file__).resolve().parent / "answers_key.json"
    try:
        with open(answers_file, "r", encoding="utf-8") as fh:
            answer_key = json.load(fh)
    except Exception:
        # If key file missing or unreadable, fall back to empty key (no correct answers)
        answer_key = {}

    def analyze_single_quiz(quiz: Quiz, answer_key: dict) -> dict:
        """Analyze one Quiz object against the answer_key.

        Returns a dict with keys: title, total_questions, score, question_details, analysis
        """
        correct_count = 0
        question_details = []

        for question in quiz.questions:
            qid = str(question.id)
            correct_index = answer_key.get(qid)
            user_ans = question.user_answer
            is_correct = (user_ans is not None and correct_index is not None and user_ans == correct_index)
            if is_correct:
                correct_count += 1

            question_details.append({
                "question_id": question.id,
                "user_answer": user_ans if user_ans is not None else "No answer",
                "correct_answer_index": correct_index if correct_index is not None else "Unknown",
                "is_correct": is_correct
            })

        analysis = f"Quiz: {quiz.title}\n"
        analysis += f"Total Questions: {len(quiz.questions)}\n"
        analysis += f"Correct Answers: {correct_count}\n"
        analysis += f"Score: {correct_count}/{len(quiz.questions)}\n\n"
        analysis += "Question Details:\n"
        for detail in question_details:
            status = "✓ Correct" if detail["is_correct"] else "✗ Incorrect"
            analysis += f"Q{detail['question_id']}: {status}\n"
            analysis += f"  Your answer: {detail['user_answer']}\n"
            if not detail["is_correct"]:
                ca = detail.get('correct_answer_index', 'Unknown')
                analysis += f"  Correct answer index: {ca}\n"

        return {
            "title": quiz.title,
            "total_questions": len(quiz.questions),
            "score": correct_count,
            "question_details": question_details,
            "analysis": analysis,
        }

    total_questions = 0
    total_correct = 0
    combined_question_details = []
    per_quiz_summary = []
    combined_analysis_parts = []

    # Determine whether the answers file contains per-quiz objects (nested dicts)
    nested_answers = False
    if isinstance(answer_key, dict):
        nested_answers = any(isinstance(v, dict) for v in answer_key.values())

    def _select_answer_map_for_quiz(quiz: Quiz):
        # If answers are flat, just return them
        if not nested_answers:
            return answer_key
        # Try to match by normalized title (prefer exact normalized equality, then substring)
        def normalize(s: str) -> str:
            return ''.join(ch for ch in (s or "").lower() if ch.isalnum())

        title_norm = normalize(quiz.title or "")
        # 1) exact normalized match
        for k, v in answer_key.items():
            if not isinstance(v, dict):
                continue
            if title_norm and normalize(k) == title_norm:
                return v

        # 2) substring match (either direction)
        for k, v in answer_key.items():
            if not isinstance(v, dict):
                continue
            k_norm = normalize(k)
            if title_norm and (k_norm in title_norm or title_norm in k_norm):
                return v

        # 3) If no title match, pick the first mapping that contains any of the question ids
        for k, v in answer_key.items():
            if not isinstance(v, dict):
                continue
            for qobj in quiz.questions:
                if str(qobj.id) in v:
                    return v

        # 4) Fallback: merge all nested maps into one
        merged = {}
        for v in answer_key.values():
            if isinstance(v, dict):
                merged.update(v)
        return merged

    for qi, q in enumerate(quizzes, start=1):
        quiz_answer_map = _select_answer_map_for_quiz(q)
        single = analyze_single_quiz(q, quiz_answer_map)
        # attach quiz index to each question detail for traceability
        for d in single["question_details"]:
            d["quiz_index"] = qi
        combined_question_details.extend(single["question_details"])
        per_quiz_summary.append({
            "title": single["title"],
            "total_questions": single["total_questions"],
            "score": single["score"],
            "analysis": single["analysis"],
            "question_details": single["question_details"]
        })
        combined_analysis_parts.append(single["analysis"])
        total_questions += single["total_questions"]
        total_correct += single["score"]

    state["analysis"] = "\n\n--- Per-quiz analysis ---\n\n".join(combined_analysis_parts)
    state["score"] = total_correct
    state["total_questions"] = total_questions
    state["question_details"] = combined_question_details
    state["per_quiz_summary"] = per_quiz_summary

    return state


def apply_guardrails(state: QuizState) -> QuizState:
    # Patterns in English kept for backward-compatibility; add Romanian equivalents too
    harmful_patterns = [
        "stupid", "dumb", "idiot", "failure", "worthless", "hopeless",
        "give up", "terrible", "awful", "pathetic", "loser", "incompetent",
        # Romanian
        "prost", "idiot", "incompetent", "valorii zero", "fără valoare", "prostie"
    ]
    
    negative_patterns = [
        "you failed", "you're bad", "you can't", "you'll never",
        # Romanian negative phrases
        "ai picat", "ești prost", "nu poți", "nu vei putea niciodată"
    ]
    
    analysis_lower = state["analysis"].lower()
    feedback_lower = state.get("feedback", "").lower()

    print("analysis_lower:", analysis_lower)
    print("feedback_lower:", feedback_lower)
    
    violations = []
    for pattern in harmful_patterns:
        if pattern in analysis_lower or pattern in feedback_lower:
            violations.append(f"Contains harmful language: '{pattern}'")
    
    for pattern in negative_patterns:
        if pattern in analysis_lower or pattern in feedback_lower:
            violations.append(f"Contains discouraging phrase: '{pattern}'")
    
    if violations:
        state["guardrail_check"] = f"BLOCKED: {'; '.join(violations)}"
        state["feedback"] = "Feedback generation was blocked for safety reasons. Please contact support."
    else:
        positive_indicators = ["great", "good", "excellent", "correct", "well done", "keep", "practice"]
        has_positive = any(indicator in analysis_lower or indicator in feedback_lower for indicator in positive_indicators)
        
        if state["total_questions"] > 0:
            constructive_check = has_positive or state["score"] == state["total_questions"]
            if constructive_check:
                state["guardrail_check"] = "APPROVED"
            else:
                state["guardrail_check"] = "WARNING: consider using more encouraging language"
        else:
            state["guardrail_check"] = "APPROVED"
    
    return state


def generate_feedback(state: QuizState) -> QuizState:
    if state["total_questions"] == 0:
        state["feedback"] = "Error: Cannot generate feedback for a quiz with no questions."
        return state
    
    api_key = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")
    
    if api_key == "YOUR_OPENROUTER_API_KEY_HERE" or not api_key:
        # concise fallback behavior: short celebration if all correct, otherwise 2-3 short sentences
        total = state['total_questions']
        score = state['score']

        # Try to load per-quiz topic maps from topics_by_quiz.json; fall back to an inline map if missing.
        topics_file = pathlib.Path(__file__).resolve().parent / "topics_by_quiz.json"
        try:
            with open(topics_file, "r", encoding="utf-8") as fh:
                topics_by_quiz = json.load(fh)
        except Exception:
            topics_by_quiz = None

        # Helper to normalize titles for matching
        def normalize(s: str) -> str:
            return ''.join(ch for ch in (s or "").lower() if ch.isalnum())

        # Select topic maps per-quiz by matching the quiz title included in the incoming request.
        # Build a mapping: quiz_index -> { question_id: topic }
        quiz_topics = {}

        def select_topic_map_by_title(title: str):
            title_norm = normalize(title)
            if not isinstance(topics_by_quiz, dict):
                return {}
            # if nested per-quiz maps
            if any(isinstance(v, dict) for v in topics_by_quiz.values()):
                # 1) exact normalized match
                for k, v in topics_by_quiz.items():
                    if not isinstance(v, dict):
                        continue
                    if title_norm and normalize(k) == title_norm:
                        return {int(k2): str(v2) for k2, v2 in v.items()}
                # 2) substring match
                for k, v in topics_by_quiz.items():
                    if not isinstance(v, dict):
                        continue
                    k_norm = normalize(k)
                    if title_norm and (k_norm in title_norm or title_norm in k_norm):
                        return {int(k2): str(v2) for k2, v2 in v.items()}
                # 3) no match
                return {}
            else:
                # flat mapping
                try:
                    return {int(k): str(v) for k, v in topics_by_quiz.items()}
                except Exception:
                    return {}

        # prefer explicit quizzes list in state; otherwise use single quiz title
        if "quizzes" in state and isinstance(state["quizzes"], list):
            for idx, quiz_obj in enumerate(state["quizzes"], start=1):
                title = None
                if hasattr(quiz_obj, "title"):
                    title = getattr(quiz_obj, "title")
                elif isinstance(quiz_obj, dict):
                    title = quiz_obj.get("title")
                quiz_topics[idx] = select_topic_map_by_title(title)
        elif "quiz" in state and state["quiz"] is not None:
            qobj = state["quiz"]
            title = getattr(qobj, "title") if hasattr(qobj, "title") else (qobj.get("title") if isinstance(qobj, dict) else None)
            quiz_topics[1] = select_topic_map_by_title(title)

        def default_topics():
            return {
                1: "conservation of momentum",
                2: "elastic collisions and kinetic energy conservation",
                3: "energy dissipation (heat & deformation)",
                4: "effects of mass ratio in collisions",
                5: "coefficient of restitution and velocity ratios",
            }

        if score == total:
            # very short celebration (English)
            state["feedback"] = f"Excellent — all {total} answers are correct. Well done!"
            return state

        # otherwise build 2-3 short sentences
        incorrect = [d for d in state['question_details'] if not d['is_correct']]
        missed_ids = [str(d['question_id']) for d in incorrect]
        # gather unique topic suggestions; select topic by the question's quiz_index to avoid mixing
        suggested = []
        for d in incorrect:
            tid = d['question_id']
            qidx = d.get('quiz_index', 1)
            topic_map_for_quiz = quiz_topics.get(qidx) or {}
            topic = topic_map_for_quiz.get(tid)
            if not topic:
                topic = default_topics().get(tid)
            if topic and topic not in suggested:
                suggested.append(topic)

        sentence1 = f"Score: {score}/{total}."
        if suggested:
            # join 1-2 main topics for brevity
            top_suggestions = ", ".join(suggested[:2])
            sentence2 = f"Review: {top_suggestions}."
        else:
            sentence2 = "Review the topics you missed."
        sentence3 = "Try again after reviewing the concepts."

        state["feedback"] = " ".join([sentence1, sentence2, sentence3])
        return state
    
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model="meta-llama/llama-3.2-3b-instruct:free",
        temperature=0.7
    )
    
    system_prompt = """You are a concise educational tutor. Provide feedback in 2-3 short sentences.
If all answers are correct, reply with a single short celebratory sentence (e.g. "Excellent — all answers are correct!").
If there are incorrect answers, briefly state the score, name up to two key topics to review (based on the provided mapping), and finish with a short encouraging sentence.
Always use a positive, supportive tone and keep replies very short.
Responses MUST be in ENGLISH.
"""

    # Provide the analysis and a mapping from question IDs to suggested review topics so the model can reference them.
    topic_map_lines = []
    topic_map = {
        1: "conservation of momentum",
        2: "elastic collisions and conservation of kinetic energy",
        3: "energy dissipation (heat & deformation)",
        4: "effects of mass ratio in collisions",
        5: "coefficient of restitution and velocity ratios",
    }
    for k, v in topic_map.items():
        topic_map_lines.append(f"Q{k}: {v}")

    user_prompt = f"""Please provide concise feedback for this quiz submission (2-3 short sentences).

Quiz analysis:
{state['analysis']}

If there are incorrect answers, use the mapping below to suggest topics to review (choose up to two):
{chr(10).join(topic_map_lines)}

Rules:
- If all answers are correct: return a single short celebratory sentence.
- If some answers are incorrect: mention the score in one short sentence, suggest up to two topics in one short sentence, and finish with a short encouraging sentence.

RESPONSES MUST BE IN ENGLISH.
"""
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        state["feedback"] = str(response.content)
    except Exception:
        # Do not expose internal error details to the frontend. Provide a friendly fallback message
        # and include the quiz analysis so the user still sees results.
        state["feedback"] = "Our AI isn't available at the moment — here are your quiz results:\n\n" + state.get('analysis', 'No analysis available.')
    
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
