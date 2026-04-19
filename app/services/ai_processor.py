import os
import json
import redis
from groq import Groq


# Redis Setup (FAIL SAFE)

redis_url = os.getenv("REDIS_URL")

redis_client = None

if redis_url:
    try:
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            ssl_cert_reqs=None  # required for Upstash / Render Redis
        )
    except Exception as e:
        print("Redis init failed:", e)
        redis_client = None
else:
    print("REDIS_URL not set — caching disabled")


# Groq Setup

groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key) if groq_api_key else None

if not client:
    print("GROQ_API_KEY not set — AI will fail safely")



# DEFAULT RESPONSE SHAPE

def empty_response(message=""):
    return {
        "score": 0,
        "summary": message or "No analysis available",
        "strengths": [],
        "weaknesses": [],
        "improvements": []
    }



# SAFE JSON PARSER

def safe_json_parse(content: str):
    if not content or not content.strip():
        raise ValueError("Empty AI response")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("❌ Invalid JSON from AI:\n", content)
        raise ValueError("AI returned invalid JSON")



# MAIN FUNCTION

def analyze_with_ai(text: str):
    if not text:
        return empty_response("No input text provided")

    cache_key = f"resume:{abs(hash(text))}"

    # -----------------------------
    # 1. Redis cache (safe)
    # -----------------------------
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print("Redis read error:", e)

    
    # 2. AI unavailable
  
    if not client:
        return empty_response("AI service not configured")

   
    # 3. Groq AI Call (UPDATED MODEL)

    try:
        prompt = f"""
You are a resume analysis AI.

Return ONLY valid JSON (no markdown, no explanation).

Format:
{{
  "score": 0-100,
  "summary": "...",
  "strengths": [],
  "weaknesses": [],
  "improvements": []
}}

Resume:
{text}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[
                {"role": "system", "content": "You MUST return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        print("AI RAW RESPONSE:", content)

        result = safe_json_parse(content)

    
        # 4. Ensure safe schema (prevents KeyError later)
     
        safe_result = {
            "score": result.get("score", 0),
            "summary": result.get("summary", ""),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "improvements": result.get("improvements", [])
        }

        # -----------------------------
        # 5. Cache result
        # -----------------------------
        if redis_client:
            try:
                redis_client.set(cache_key, json.dumps(safe_result), ex=3600)
            except Exception as e:
                print("Redis write error:", e)

        return safe_result

    except Exception as e:
        print("AI processing failed:", e)
        return empty_response("AI analysis failed")