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
    analysis: str
    feedback: str
    score: int
    total_questions: int
    question_details: list
    guardrail_check: str


def analyze_quiz(state: QuizState) -> QuizState:
    quiz = state["quiz"]
    
    if not quiz.questions or len(quiz.questions) == 0:
        state["analysis"] = "Eroare: testul nu conține întrebări"
        state["score"] = 0
        state["total_questions"] = 0
        state["question_details"] = []
        return state
    
    # Load canonical answers from answers_key.json (mapping question_id -> correct answer index)
    answers_file = pathlib.Path(__file__).resolve().parent / "answers_key.json"
    try:
        with open(answers_file, "r", encoding="utf-8") as fh:
            answer_key = json.load(fh)
    except Exception:
        # If key file missing or unreadable, fall back to empty key (no correct answers)
        answer_key = {}

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
    
    state["analysis"] = analysis
    state["score"] = correct_count
    state["total_questions"] = len(quiz.questions)
    state["question_details"] = question_details
    
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
    
    violations = []
    for pattern in harmful_patterns:
        if pattern in analysis_lower or pattern in feedback_lower:
            violations.append(f"Conține limbaj dăunător: '{pattern}'")
    
    for pattern in negative_patterns:
        if pattern in analysis_lower or pattern in feedback_lower:
            violations.append(f"Conține o expresie descurajantă: '{pattern}'")
    
    if violations:
        state["guardrail_check"] = f"BLOCAT: {'; '.join(violations)}"
        state["feedback"] = "Generarea feedback-ului a fost blocată din motive de siguranță. Vă rugăm să contactați asistența."
    else:
        positive_indicators = ["great", "good", "excellent", "correct", "well done", "keep", "practice"]
        has_positive = any(indicator in analysis_lower or indicator in feedback_lower for indicator in positive_indicators)
        
        if state["total_questions"] > 0:
            constructive_check = has_positive or state["score"] == state["total_questions"]
            if constructive_check:
                state["guardrail_check"] = "APROBAT"
            else:
                state["guardrail_check"] = "AVERTISMENT: Luați în considerare adăugarea unui limbaj mai încurajator"
        else:
            state["guardrail_check"] = "APPROVED"
    
    return state


def generate_feedback(state: QuizState) -> QuizState:
    if state["total_questions"] == 0:
        state["feedback"] = "Error: Cannot generate feedback for a quiz with no questions."
        return state
    
    api_key = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")
    
    if api_key == "YOUR_OPENROUTER_API_KEY_HERE" or not api_key:
    # concise fallback behavior: short celebration if all correct, otherwise 2-3 short sentences (Romanian)
        total = state['total_questions']
        score = state['score']

        # map question ids to suggested topics for quick review
        topics_by_qid = {
            1: "conservation of momentum",
            2: "elastic collisions and kinetic energy conservation",
            3: "energy dissipation (heat & deformation)",
            4: "effects of mass ratio in collisions",
            5: "coefficient of restitution and velocity ratios",
            6: "perfectly inelastic collisions",
            7: "vector vs scalar quantities (momentum)",
            8: "applying conservation on each axis for vector quantities",
            9: "elastic collision outcomes for equal masses",
            10: "energy loss when restitution e < 1"
        }

        if score == total:
            # very short celebration (Romanian)
            state["feedback"] = f"Excelent — toate cele {total} răspunsuri sunt corecte. Bravo!"
            return state

        # otherwise build 2-3 short sentences
        incorrect = [d for d in state['question_details'] if not d['is_correct']]
        missed_ids = [str(d['question_id']) for d in incorrect]
        # gather unique topic suggestions
        suggested = []
        for d in incorrect:
            tid = d['question_id']
            topic = topics_by_qid.get(tid)
            if topic and topic not in suggested:
                suggested.append(topic)

        sentence1 = f"Scor: {score}/{total}."
        if suggested:
            # join 1-2 main topics for brevity
            top_suggestions = ", ".join(suggested[:2])
            sentence2 = f"Revizuiește: {top_suggestions}."
        else:
            sentence2 = "Revizuiește subiectele la care ai greșit."
        sentence3 = "Încearcă din nou după ce revizuiești conceptele."

        state["feedback"] = " ".join([sentence1, sentence2, sentence3])
        return state
        return state
    
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model="meta-llama/llama-3.2-3b-instruct:free",
        temperature=0.7
    )
    
    system_prompt = """Ești un tutor educațional concis. Oferă feedback în 2-3 propoziții scurte.
Dacă toate răspunsurile sunt corecte, răspunde cu o singură propoziție scurtă de celebrare (de ex. "Excelent — toate răspunsurile sunt corecte!").
Dacă există răspunsuri incorecte, menționează pe scurt scorul, numește până la două subiecte cheie de revizuit (bazate pe maparea furnizată) și încheie cu o scurtă frază încurajatoare.
Folosește întotdeauna un ton pozitiv și de susținere și păstrează răspunsurile foarte scurte.
Răspunsurile TREBUIE să fie în LIMBA ROMÂNĂ.
"""

    # Provide the analysis and a mapping from question IDs to suggested review topics so the model can reference them.
    topic_map_lines = []
    topic_map = {
        1: "conservarea impulsului",
        2: "coliziuni elastice și conservarea energiei cinetice",
        3: "diziparea energiei (căldură și deformații)",
        4: "efectele raportului de mase în coliziuni",
        5: "coeficientul de restituție și rapoartele de viteze",
        6: "coliziuni perfect inelastice",
        7: "mărimi vectoriale vs scalare (impuls)",
        8: "aplicarea conservării pe fiecare axă pentru mărimi vectoriale",
        9: "rezultatele coliziunilor elastice pentru mase egale",
        10: "pierdere de energie când coeficientul e < 1"
    }
    for k, v in topic_map.items():
        topic_map_lines.append(f"Q{k}: {v}")

    user_prompt = f"""Vă rog oferiți un feedback concis pentru această trimitere de test (2-3 propoziții scurte).

Analiză test:
{state['analysis']}

Dacă există răspunsuri incorecte, folosiți maparea de mai jos pentru a sugera subiecte de revizuit (alegeți până la două):
{chr(10).join(topic_map_lines)}

Reguli:
- Dacă toate răspunsurile sunt corecte: returnați o singură propoziție scurtă de celebrare.
- Dacă unele răspunsuri sunt incorecte: menționați scorul într-o propoziție scurtă, sugerați până la două subiecte într-o propoziție scurtă și încheiați cu o scurtă frază încurajatoare.

RĂSPUNSURILE TREBUIE SĂ FIE ÎN LIMBA ROMÂNĂ.
"""
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        state["feedback"] = str(response.content)
    except Exception as e:
        state["feedback"] = f"Error generating AI feedback: {str(e)}\n\nFalling back to basic feedback:\n{state['analysis']}"
    
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
