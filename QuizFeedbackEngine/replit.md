# Quiz Feedback Service with LangGraph

## Overview

This is a FastAPI-based service that provides AI-powered feedback on quiz submissions using LangGraph workflows and LLM integration through OpenRouter. The system analyzes quiz responses, calculates scores, and generates constructive feedback using state-based workflows. It includes a fallback mode that operates without API keys for basic functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Framework
**Decision**: FastAPI for web framework  
**Rationale**: FastAPI provides automatic API documentation, built-in data validation with Pydantic, async support, and excellent performance for API-based services.

### Workflow Engine
**Decision**: LangGraph for state-based workflow management  
**Rationale**: LangGraph provides a structured approach to managing complex AI workflows with clear state transitions, making the quiz analysis process more maintainable and debuggable than linear prompt chains.

**Key Components**:
- State management through TypedDict (`QuizState`)
- Node-based processing (analyze_quiz, generate_feedback, apply_guardrails)
- State transitions through a directed graph structure

### Data Validation
**Decision**: Pydantic models for all data structures  
**Rationale**: Ensures type safety and automatic validation at API boundaries. Models include:
- `Quiz`: Container for quiz title and questions
- `Question`: Individual quiz question with multiple choice answers
- `Answer`: Answer options with correctness flags
- `QuizSubmission`: API request wrapper
- `FeedbackResponse`: Standardized feedback output

### LLM Integration
**Decision**: OpenRouter API with ChatOpenAI interface  
**Rationale**: OpenRouter provides access to multiple LLM providers through a single API, allowing model flexibility without vendor lock-in. Uses LangChain's ChatOpenAI wrapper for consistent interface.

**Features**:
- Configurable via environment variable (`OPENROUTER_API_KEY`)
- Fallback mode for development/testing without API key
- Supports multiple model backends through OpenRouter

### Content Safety
**Decision**: Guardrail system for feedback filtering  
**Rationale**: Ensures generated feedback remains constructive, educational, and appropriate. Filters out potentially harmful or inappropriate content before returning to users.

### API Design
**Decision**: RESTful endpoints with CORS support  
**Rationale**: Standard REST patterns make integration straightforward. CORS middleware enables frontend applications from any origin.

**Endpoints**:
- `POST /feedback`: Main quiz submission and analysis endpoint
- `GET /mock-quiz`: Sample quiz data for testing
- `GET /mock-quiz-2`: Additional sample quiz
- `GET /health`: Service health check with API configuration status
- `GET /`: API documentation and available endpoints

### Mock Data System
**Decision**: Pre-configured quiz examples in separate module  
**Rationale**: Enables testing and demonstration without requiring external data sources. Examples include Python programming quizzes with varied question types.

### Error Handling
**Decision**: Graceful degradation with fallback feedback  
**Rationale**: Service remains functional even without LLM API access, providing basic score calculation and generic feedback messages.

## External Dependencies

### LLM Provider
- **OpenRouter API**: Primary LLM access layer
  - Requires API key configuration
  - Supports multiple model backends
  - Used for generating personalized feedback

### Python Packages
- **langgraph**: State-based workflow orchestration
- **langchain**: LLM integration framework
- **langchain-openai**: OpenAI-compatible chat interface
- **fastapi**: Web framework and API server
- **uvicorn**: ASGI server for FastAPI
- **pydantic**: Data validation and settings management

### Infrastructure Requirements
- Environment variable support for configuration
- No database required (stateless service)
- No authentication system (open API)
- CORS enabled for cross-origin requests