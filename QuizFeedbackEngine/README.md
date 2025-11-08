# Quiz Feedback Service with LangGraph

A FastAPI service that uses LangGraph workflows to provide AI-powered feedback on quiz submissions using LLM integration via OpenRouter.

## Features

- **LangGraph Workflow**: State-based workflow for quiz analysis
- **LLM Integration**: Uses OpenRouter API to access multiple AI models
- **Guardrails**: Simple content filtering for safe and constructive feedback
- **Mock Data**: Pre-configured quiz examples for testing
- **FastAPI Endpoints**: RESTful API for easy integration
- **Fallback System**: Works without API key (basic feedback mode)

## Project Structure

```
.
├── main.py                    # FastAPI application with endpoints
├── langgraph_workflow.py      # LangGraph workflow implementation
├── models.py                  # Pydantic models for data validation
├── mock_data.py              # Sample quiz data for testing
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Setup

### 1. Install Dependencies

Dependencies are already installed:
- langgraph
- langchain
- langchain-openai
- fastapi
- uvicorn
- pydantic

### 2. Configure OpenRouter API Key

1. Get your API key from [OpenRouter](https://openrouter.ai/keys)
2. Set the environment variable:
   ```bash
   export OPENROUTER_API_KEY=your_api_key_here
   ```

**Note**: The service works without an API key in fallback mode with basic feedback.

### 3. Run the Service

```bash
python main.py
```

The service will start on `http://0.0.0.0:5000`

## API Endpoints

### GET /
Root endpoint with API information

### GET /health
Health check endpoint

### GET /mock-quiz
Returns a sample Python programming quiz

### GET /mock-quiz-2
Returns a sample general knowledge quiz

### POST /feedback
Submit a quiz for AI-powered feedback

**Request Body**:
```json
{
  "quiz": {
    "title": "Python Quiz",
    "questions": [
      {
        "id": 1,
        "question_text": "What is 2+2?",
        "answers": [
          {"text": "3", "is_correct": false},
          {"text": "4", "is_correct": true},
          {"text": "5", "is_correct": false},
          {"text": "6", "is_correct": false}
        ],
        "user_answer_index": 1
      }
    ]
  }
}
```

**Response**:
```json
{
  "overall_score": 1,
  "total_questions": 1,
  "feedback": "AI-generated feedback text...",
  "question_feedback": [
    {
      "question_id": 1,
      "question_text": "What is 2+2?",
      "user_answer": "4",
      "correct_answer": "4",
      "is_correct": true
    }
  ]
}
```

### POST /feedback/analyze-only
Analyze quiz without AI feedback (faster, no API key needed)

## LangGraph Workflow

The workflow consists of three nodes:

1. **Analyze**: Evaluates quiz answers and calculates score
2. **Guardrails**: Ensures feedback will be constructive and safe
3. **Generate Feedback**: Uses LLM to create personalized feedback

```
┌─────────┐     ┌────────────┐     ┌──────────────────┐
│ Analyze │ --> │ Guardrails │ --> │ Generate Feedback│
└─────────┘     └────────────┘     └──────────────────┘
```

## Quiz Data Format

Each quiz must have:
- **title**: String
- **questions**: Array of questions (each with 4 answers, 1 correct)
- **user_answer_index**: Index (0-3) of the selected answer

## Guardrails

The system implements simple guardrails to ensure:
- Constructive and encouraging feedback
- Educational and informative content
- Respectful and professional tone
- Focus on learning opportunities
- No harmful or discouraging language

## Example Usage

### Using cURL

```bash
# Get mock quiz
curl http://localhost:5000/mock-quiz

# Submit quiz for feedback
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "quiz": {
    "title": "Test Quiz",
    "questions": [
      {
        "id": 1,
        "question_text": "What is 2+2?",
        "answers": [
          {"text": "3", "is_correct": false},
          {"text": "4", "is_correct": true},
          {"text": "5", "is_correct": false},
          {"text": "6", "is_correct": false}
        ],
        "user_answer_index": 1
      }
    ]
  }
}
EOF
```

### Using Python

```python
import requests

response = requests.get("http://localhost:5000/mock-quiz")
quiz = response.json()

# Add user answers
quiz["questions"][0]["user_answer_index"] = 1

# Submit for feedback
feedback_response = requests.post(
    "http://localhost:5000/feedback",
    json={"quiz": quiz}
)
print(feedback_response.json())
```

## Configuration

### OpenRouter Models

The default model is `meta-llama/llama-3.2-3b-instruct:free` (free tier).

To use a different model, edit `langgraph_workflow.py`:

```python
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    model="anthropic/claude-3.5-sonnet",  # Change this
    temperature=0.7
)
```

Available models: https://openrouter.ai/models

## Integration with Your Application

This service is designed to be integrated with your application:

1. **Get Quiz Template**: `GET /mock-quiz` to see the expected format
2. **Collect User Answers**: In your app, record user selections as `user_answer_index`
3. **Submit for Feedback**: `POST /feedback` with the quiz data
4. **Display Results**: Show the feedback to users

## License

MIT
