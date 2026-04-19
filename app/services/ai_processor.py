import os
import json
import redis
from groq import Groq

# -----------------------------
# Redis Setup (FAIL SAFE)
# -----------------------------
redis_url = os.getenv("REDIS_URL")

redis_client = None

if redis_url:
    try:
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            ssl_cert_reqs=None  # important for Upstash/Render Redis
        )
    except Exception as e:
        print("Redis init failed:", e)
        redis_client = None
else:
    print("REDIS_URL not set — caching disabled")


# -----------------------------
# Groq Setup
# -----------------------------
groq_api_key = os.getenv("GROQ_API_KEY")

client = None

if groq_api_key:
    client = Groq(api_key=groq_api_key)
else:
    print("GROQ_API_KEY not set — AI will fail safely")


# -----------------------------
# SAFE JSON PARSER
# -----------------------------
def safe_json_parse(content: str):
    if not content or not content.strip():
        raise ValueError("Empty AI response")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("❌ Invalid JSON from AI:", content)
        raise ValueError("AI returned invalid JSON")


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def analyze_with_ai(text: str):
    if not text:
        return {
            "score": 0,
            "summary": "No input text provided",
            "strengths": [],
            "weaknesses": [],
            "improvements": []
        }

    cache_key = f"resume:{hash(text)}"

    # -----------------------------
    # 1. Try Redis cache (safe)
    # -----------------------------
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print("Redis read error:", e)

    # -----------------------------
    # 2. Check AI availability
    # -----------------------------
    if not client:
        return {
            "score": 0,
            "summary": "AI service not configured",
            "strengths": [],
            "weaknesses": [],
            "improvements": []
        }

    # -----------------------------
    # 3. Call Groq AI
    # -----------------------------
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
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a strict JSON generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        print("AI RAW RESPONSE:", content)

        result = safe_json_parse(content)

        # -----------------------------
        # 4. Cache result (safe)
        # -----------------------------
        if redis_client:
            try:
                redis_client.set(cache_key, json.dumps(result), ex=3600)
            except Exception as e:
                print("Redis write error:", e)

        return result

    except Exception as e:
        print("AI processing failed:", e)

        return {
            "score": 0,
            "summary": "AI analysis failed",
            "strengths": [],
            "weaknesses": [],
            "improvements": []
        }