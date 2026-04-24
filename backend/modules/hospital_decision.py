import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def check_go_or_stay(text: str) -> dict:
    prompt = f"""You are a medical AI assistant for Pakistani users. The user may write in English or Roman Urdu.

Based on these symptoms: "{text}"

Respond in JSON only. No extra text, no markdown, no explanation outside the JSON.

{{
  "verdict": "GO" or "STAY",
  "urgency": "Immediate" or "Within 24hrs" or "Can wait",
  "reasons": ["reason1", "reason2", "reason3"],
  "disclaimer": "This is not a substitute for professional medical advice."
}}

Rules:
- verdict is GO if symptoms suggest something serious, emergency, or worsening
- verdict is STAY if symptoms are mild and manageable at home
- always provide exactly 3 reasons
- reasons should be in simple plain language a non-doctor can understand
- if the user wrote in Roman Urdu or Urdu, respond with reasons, urgency and disclaimer in Roman Urdu
- if the user wrote in English, respond in English
- verdict field must always stay as "GO" or "STAY" in English regardless of input language"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # best free model for instruction following
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)