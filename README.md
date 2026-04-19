# AI Resume Analyzer - Python Microservice
This is the **Python-based AI microservice** for the AI Resume Analyzer platform.
It handles:
- Resume text processing
- AI-powered analysis using Groq
- Redis caching for performance optimization
- Structured JSON response generation for the backend

## Tech Stack
- Python 3.11
- FastAPI
- Groq API (LLM inference)
- Redis (caching layer)
- Uvicorn (ASGI server)

## Architecture
This service is part of a distributed system:

Frontend (Next.js)
↓
ASP.NET Core Backend
↓
Python FastAPI Service
↓
Groq API
↓
Redis Cache

The backend sends extracted resume text to this service, which returns structured AI analysis.

## AI Provider (Groq)
This project uses **Groq API** instead of OpenAI for fast, low-cost inference.
Model used:
- `llama3-8b-8192`
Groq provides:
- High-speed inference
- Free tier access (depending on plan)
- OpenAI-compatible API structure

## Features
### 1. Resume Analysis Endpoint
Analyzes resume text and returns:
```json
{
  "summary": "...",
  "atsScore": 85,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "improvements": ["..."]
}


2. Redis Caching

To improve performance and reduce API costs:

* Each resume input is hashed
* Results are cached in Redis
* Cache expiry: 1 hour

This ensures:

* Faster repeat analysis
* Reduced Groq API calls
* Lower cost + better performance


API Endpoints

POST /analyze

Analyzes resume text.

Request:

{
  "text": "resume content here"
}

Response:

{
  "summary": "...",
  "atsScore": 80,
  "strengths": [],
  "weaknesses": [],
  "improvements": []
}


Environment Variables

Create a .env file or configure in Render:

GROQ_API_KEY=your-groq-api-key
REDIS_URL=your-redis-connection-string



Running Locally (Optional)

Install dependencies:

pip install -r requirements.txt

Run server:

uvicorn app.main:app --reload --port 8000

Service runs at:

http://localhost:8000


Deployment (Render)

This service is deployed as a Web Service on Render.

Build Command:

pip install -r requirements.txt

Start Command:

uvicorn app.main:app --host 0.0.0.0 --port 10000


Integration

This service is consumed by the ASP.NET Core backend via:

PythonService__BaseUrl=https://your-render-url.onrender.com


Key Design Decisions

Why Groq?

* Faster inference than traditional APIs
* Lower cost
* OpenAI-compatible SDK
* Suitable for real-time resume scoring

Why Redis?

* Avoid repeated AI calls
* Improve response speed
* Reduce API cost significantly
* Cache identical resume inputs

Project Impact

This microservice enables:

* Scalable AI processing
* Clean separation of concerns
* Production-style backend architecture
* Cost-optimized AI usage


Author: Simba Chasumba

Built as part of an AI Resume Analyzer system using:

* ASP.NET Core backend
* Python FastAPI AI microservice
* Groq LLM inference
* Redis caching layer