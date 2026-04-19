import os
import json
import hashlib
import redis
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

CACHE_EXPIRY = 3600


def get_cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()


def analyze_with_ai(text):

    key = get_cache_key(text)

    cached = redis_client.get(key)

    if cached:
        return json.loads(cached)

    prompt = f"""
Return STRICT JSON:

summary: string
strengths: string[]
weaknesses: string[]
atsScore: number
improvements: string[]

Resume:
{text[:3000]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    result = json.loads(content)

    redis_client.setex(
        key,
        CACHE_EXPIRY,
        json.dumps(result)
    )

    return result