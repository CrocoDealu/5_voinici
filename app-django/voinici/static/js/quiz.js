// Minimal frontend integration for QuizFeedbackEngine
// - Fetches mock quiz from QuizFeedbackEngine running at http://localhost:5000
// - Renders questions, captures answers, and POSTs compact attempt to /feedback/simple
// - Shows feedback in the page


// Backend endpoint for feedback. Browsers cannot connect to 0.0.0.0; use localhost instead.
// If you need to point to a different host, set window.QFE_API_BASE before this script runs.
const API_BASE = window.QFE_API_BASE || 'http://127.0.0.1:5000'; // change if your service runs elsewhere


async function fetchQuiz() {
  const res = await fetch(`/static/quiz-data/${quizFile}`);
  if (!res.ok) throw new Error('Failed to load quiz');
  const quiz = await res.json();
  window.__embeddedQuiz = quiz;
  return quiz;
}


function renderQuiz(quiz) {
  const container = document.getElementById('quiz-container');
  container.innerHTML = '';


  const title = document.createElement('h2');
  title.textContent = quiz.title || 'Quiz';
  container.appendChild(title);


  const form = document.createElement('form');
  form.id = 'quiz-form';


  quiz.questions.forEach((q, idx) => {
    const wrap = document.createElement('div');
    wrap.className = 'mb-3';
    wrap.classList.add('question');
    wrap.dataset.qidx = idx;


    const qn = document.createElement('div');
    qn.className = 'question-text';
    qn.innerHTML = `<strong>Q${idx + 1}:</strong> ${q.text}`;
    wrap.appendChild(qn);


    if (q.answers && q.answers.length) {
      const answersDiv = document.createElement('div');
      answersDiv.className = 'answers';
      q.answers.forEach((a, ai) => {
        const id = `q_${idx}_a_${ai}`;
        const label = document.createElement('label');
        label.className = 'd-block';
        // Use a span for answer text so we can style the label and text separately
        label.innerHTML = `
          <input type="radio" name="q_${idx}" value="${ai}" id="${id}"> <span class="answer-text">${a.text}</span>
        `;
        // Add change handler to toggle selected class on the label
        const input = label.querySelector('input[type="radio"]');
        input.addEventListener('change', () => {
          // remove selected from other labels in this answersDiv
          answersDiv.querySelectorAll('label').forEach(l => l.classList.remove('selected'));
          if (input.checked) label.classList.add('selected');
          // remove unanswered marker from question wrapper when an option is selected
          const qwrap = label.closest('.question');
          if (qwrap) qwrap.classList.remove('unanswered');
        });


        // If this radio is pre-checked, mark the label
        if (input.checked) label.classList.add('selected');


        answersDiv.appendChild(label);
      });
      wrap.appendChild(answersDiv);
    } else {
      // free text
      const input = document.createElement('input');
      input.type = 'text';
      input.name = `q_${idx}`;
      input.className = 'form-control';
      wrap.appendChild(input);
    }


    // store question id in data attribute for compact submission
    wrap.dataset.qid = q.id || '';


    form.appendChild(wrap);
  });


  container.appendChild(form);
  document.getElementById('submit-btn').disabled = false;
}


function collectAttempt(quiz) {
  const form = document.getElementById('quiz-form');
  const answers = [];


  quiz.questions.forEach((q, idx) => {
    const qid = q.id || null;
    const name = `q_${idx}`;
    const radios = form.querySelectorAll(`input[name="${name}"]`);
    let user_index = null;
    if (radios && radios.length) {
      radios.forEach(r => { if (r.checked) user_index = parseInt(r.value, 10); });
    } else {
      const input = form.querySelector(`input[name="${name}"]`);
      if (input) user_index = input.value || '';
    }


    answers.push({
      id: qid,
      text: q.text,
      options: q.answers.map(a => a.text),
      correct_answer: q.correct_answer,  // include correct answer index from JSON
      user_answer: user_index
    });
  });


  return {
    title: quiz.title,
    questions: answers
  };
}


function validateAllAnswered(quiz) {
  const form = document.getElementById('quiz-form');
  const unanswered = [];
  quiz.questions.forEach((q, idx) => {
    const name = `q_${idx}`;
    const radios = form.querySelectorAll(`input[name="${name}"]`);
    if (radios && radios.length) {
      let any = false;
      radios.forEach(r => { if (r.checked) any = true; });
      if (!any) unanswered.push(idx);
    } else {
      const input = form.querySelector(`input[name="${name}"]`);
      if (input && String(input.value).trim() === '') unanswered.push(idx);
    }
  });
  return unanswered;
}


async function submitAttempt(attempt) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    // Wrap attempt under top-level "quiz"
    body: JSON.stringify({ quiz: attempt })
  });
  if (!res.ok) throw new Error('AI_UNAVAILABLE');
  return res.json();
}


const urlParams = new URLSearchParams(window.location.search);
const quizFile = urlParams.get('quiz') || 'collision_quiz.json';


async function init() {
  try {
    const quiz = await fetchQuiz();
    window.__currentQuiz = quiz;
    renderQuiz(quiz);


    document.getElementById('submit-btn').addEventListener('click', async () => {
      try {
        // Validate all questions answered
        const unanswered = validateAllAnswered(quiz);
        // clear previous unanswered markers
        document.querySelectorAll('.question.unanswered').forEach(e => e.classList.remove('unanswered'));
        if (unanswered.length) {
          // mark unanswered questions and show message
          unanswered.forEach(i => {
            const qwrap = document.querySelector(`.question[data-qidx="${i}"]`);
            if (qwrap) qwrap.classList.add('unanswered');
          });
          document.getElementById('feedback').textContent = `Please answer all questions (${unanswered.length} unanswered)`;
          // scroll to first unanswered
          const first = document.querySelector('.question.unanswered');
          if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
          return;
        }


        document.getElementById('submit-btn').disabled = true;
        document.getElementById('feedback').textContent = 'Submitting…';
        const attempt = collectAttempt(quiz);
        const resp = await submitAttempt(attempt);

        // ----- Option 2 integration: show overall feedback + annotate each question inline -----

        // Show overall feedback text at the top (keep existing behavior)
        const feedbackText = (resp && resp.feedback) ? resp.feedback : JSON.stringify(resp, null, 2);
        document.getElementById('feedback').textContent = feedbackText;

        // Annotate each question inline with correctness
        if (resp && Array.isArray(resp.question_feedback)) {
          let firstIncorrectAdded = false;

          resp.question_feedback.forEach((qf, i) => {
            // Map response item to rendered question index:
            // 1) prefer question_id match; 2) fall back to array index
            let idx = i;
            if (qf.question_id != null && quiz && Array.isArray(quiz.questions)) {
              const found = quiz.questions.findIndex(q => String(q.id) === String(qf.question_id));
              if (found !== -1) idx = found;
            }

            const qDiv = document.querySelector(`.question[data-qidx="${idx}"]`);
            if (!qDiv) return;

            // Remove any previous marker
            const old = qDiv.querySelector('.q-result');
            if (old) old.remove();

            // Build a new marker
            const marker = document.createElement('div');
            marker.className = 'q-result mt-2';
            marker.style.fontWeight = '600';

            if (qf.is_correct) {
              marker.style.color = '#22c55e';
              marker.textContent = '✓ Correct';
            } else {
              marker.style.color = '#ef4444';

              // Try to show the correct answer text; fall back to index if necessary
              const correctIdx = qf.correct_answer_index;
              let correctText = qf.correct_answer_text || null;
              if (!correctText && quiz && quiz.questions[idx] && Array.isArray(quiz.questions[idx].options)) {
                if (typeof correctIdx === 'number' && quiz.questions[idx].options[correctIdx] != null) {
                  correctText = quiz.questions[idx].options[correctIdx];
                }
              }

              marker.textContent = `✗ Wrong. Correct: ${correctText ?? `option ${correctIdx}`}`;

              // Optionally scroll the first incorrect into view for visibility
              if (!firstIncorrectAdded) {
                qDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstIncorrectAdded = true;
              }
            }

            qDiv.appendChild(marker);
          });
        }

        // ----- end Option 2 -----

      } catch (err) {
        // Don't show internal error or raw response to the user. Show a friendly message instead.
        document.getElementById('feedback').textContent = "Our AI isn't available at the moment";
      } finally {
        document.getElementById('submit-btn').disabled = false;
      }
    });


    document.getElementById('clear-btn').addEventListener('click', () => {
      const form = document.getElementById('quiz-form');
      if (!form) return;
      form.querySelectorAll('input[type=radio]').forEach(r => r.checked = false);
      form.querySelectorAll('label').forEach(l => l.classList.remove('selected'));
      form.querySelectorAll('input[type=text]').forEach(i => i.value = '');
      document.getElementById('feedback').textContent = '(no feedback yet)';
      // Clear inline result markers
      document.querySelectorAll('.q-result').forEach(el => el.remove());
      // Clear unanswered markers
      document.querySelectorAll('.question.unanswered').forEach(e => e.classList.remove('unanswered'));
    });
  } catch (err) {
    document.getElementById('quiz-container').textContent = 'Could not load quiz: ' + err.message;
  }
}


init();
