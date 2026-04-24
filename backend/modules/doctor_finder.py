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
      "name": "Most appropriate first doctor to see",
      "match_percentage": "Calculate based on symptom relevance. For common/vague symptoms like headache, fever, cough, cold, body ache - General Physician (95-98%). For specific symptoms - the relevant specialist (85-95%)",
      "description": "One line about what this doctor treats",
      "why_saves_money": "Why starting with this doctor saves money. Mention PKR amounts.",
      "avg_fee_pkr": "Realistic fee range in Pakistani cities in PKR"
    }},
    {{
      "name": "Specialist to see if symptoms persist or for second opinion",
      "match_percentage": "Typically 70-85 for the specialist relevant to main symptom",
      "description": "One line about what this specialist treats",
      "why_saves_money": "When and why to see this specialist. Mention PKR amounts.",
      "avg_fee_pkr": "Realistic fee range in Pakistani cities in PKR"
    }}
  ],
  "why_this_saves_you_money": [
    "specific point 1 with PKR amount",
    "specific point 2 with PKR amount",
    "specific point 3 with PKR amount"
  ],
  "disclaimer": "This is not a substitute for professional medical advice."
}}

SYMPTOM-SPECIALIST MAPPING RULES:

COMMON SYMPTOMS (start with General Physician):
- Headache, fever, cough, cold, flu, body ache, weakness, nausea → General Physician FIRST
- General body pain, tiredness, mild symptoms → General Physician
- Multiple unrelated symptoms → General Physician

SPECIFIC SYMPTOMS (may need specialist):
- Severe headache + vision problems → Neurologist
- Severe headache + vomiting + neck stiffness → Neurologist
- Ear pain, hearing loss, sinus issues → ENT Specialist
- Chest pain, breathing difficulty → Pulmonologist/Cardiologist
- Stomach pain, digestion issues → Gastroenterologist
- Skin rashes, allergies → Dermatologist
- Child symptoms → Pediatrician
- Women's health → Gynecologist

PAKISTAN-SPECIFIC GUIDELINES:
- General Physician fee: Rs. 500-1500
- Specialists fee: Rs. 1000-3000
- Always recommend General Physician first for common/vague symptoms
- Neurologist is for brain/nervous system issues, NOT for regular headaches
- ENT is for ear/nose/throat, NOT for headache

Rules:
- Return exactly 2 doctors - first should be appropriate starting point
- For headache + fever: First=General Physician (95%), Second=Internal Medicine or relevant specialist based on severity
- match_percentage must be different for both - first always higher
- specialist names must be types available in Pakistani cities
- avg_fee_pkr must reflect realistic Pakistani market rates
- why_this_saves_you_money must have exactly 3 bullet points with PKR amounts
- if user wrote in Roman Urdu/Urdu, respond in Roman Urdu
- if user wrote in English, respond in English
- specialist name field always in English"""

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
        mp = specialist["match_percentage"]
        if isinstance(mp, str):
            # Remove % if present and convert to int
            mp = mp.replace('%', '').strip()
        try:
            specialist["match_percentage"] = int(float(mp))
        except (ValueError, TypeError):
            specialist["match_percentage"] = 75  # fallback

    return parsed