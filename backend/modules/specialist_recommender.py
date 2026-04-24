import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def recommend_specialist(text: str) -> dict:
    prompt = f"""You are a medical AI assistant for Pakistani users. The user may write in English or Roman Urdu.

Based on these symptoms: "{text}"

Respond in JSON only. No extra text, no markdown, no explanation outside the JSON.

{{
  "summary": "Brief sentence summarizing the detected symptoms in plain language",
  "specialists": [
    {{
      "name": "Most relevant specialist type for these exact symptoms",
      "match_percentage": "Calculate this honestly based on how closely this specialist matches the symptoms. If symptoms are very clear and specific give 90-98. If symptoms are vague or overlapping give 70-85.",
      "description": "One line about what this specialist treats",
      "why_saves_money": "Why seeing this specialist directly saves money vs wrong referrals. Mention PKR amounts.",
      "avg_fee_pkr": "Realistic fee range for this specialist in Pakistani cities in PKR"
    }},
    {{
      "name": "Second most relevant specialist for the same symptoms — not General Physician unless truly necessary",
      "match_percentage": "Calculate honestly. Should be lower than first specialist but still relevant. Typically 60-84.",
      "description": "One line about what this specialist treats",
      "why_saves_money": "Why this is a valid alternative and how it saves money. Mention PKR amounts.",
      "avg_fee_pkr": "Realistic fee range for this specialist in Pakistani cities in PKR"
    }}
  ],
  "why_this_saves_you_money": [
    "specific point 1 with PKR amount",
    "specific point 2 with PKR amount",
    "specific point 3 with PKR amount"
  ],
  "disclaimer": "This is not a substitute for professional medical advice."
}}

Rules:
- Always return exactly 2 specialists both directly relevant to the symptoms provided
- Both specialists must be for the same disease or symptom cluster
- Never default to General Physician as second option unless symptoms are truly too vague for any specialist
- match_percentage must be calculated dynamically based on actual symptom-to-specialist relevance:
    * 90-98: symptoms are very specific and clearly point to this specialist
    * 75-89: symptoms moderately match this specialist
    * 60-74: symptoms could belong to this specialist but are not conclusive
- match_percentage must be different for both specialists — first must always be higher than second
- specialist names must be types commonly available in Pakistani cities like Karachi, Lahore, Islamabad
- avg_fee_pkr must reflect realistic current Pakistani market rates for that specific specialist type
- why_this_saves_you_money must always have exactly 3 bullet points with PKR amounts mentioned
- if the user wrote in Roman Urdu or Urdu, respond with summary, description, why_saves_money, why_this_saves_you_money and disclaimer in Roman Urdu
- if the user wrote in English, respond in English
- specialist name field must always be in English regardless of input language"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    clean = re.sub(r"```json|```", "", raw).strip()
    parsed = json.loads(clean)

    # ensure match_percentage is always an integer not a string
    for specialist in parsed.get("specialists", []):
        specialist["match_percentage"] = int(specialist["match_percentage"])

    return parsed