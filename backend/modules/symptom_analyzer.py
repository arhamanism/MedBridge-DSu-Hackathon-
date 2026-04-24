import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def check_symptoms(text: str) -> dict:
    # First, check if input contains actual medical symptoms
    validation_prompt = f"""You are a medical input validator for a Pakistani healthcare app.

Analyze this user input: "{text}"

Determine if this input contains actual medical symptoms, health complaints, or physical complaints that need diagnosis.

Greetings like "hello", "hi", "aoa", "assalamualaikum", "good morning" are NOT symptoms.
Small talk like "how are you", "what's up" is NOT symptoms.
Random words without medical meaning are NOT symptoms.

Return ONLY a JSON object in this exact format:
{{
  "is_medical": true or false,
  "detected_symptoms": "brief description of what symptoms were found, or null if none",
  "response_message": "If not medical, provide a friendly message asking for symptoms in the same language as input (English or Roman Urdu). If medical, return null."
}}

Examples:
- Input: "hello" → is_medical: false, response_message: "Hello! Please tell me what symptoms you're experiencing so I can help you."
- Input: "aoa" → is_medical: false, response_message: "Waalaikumsalam! Kya symptoms hain aapko?"
- Input: "mujhe headache hai" → is_medical: true, detected_symptoms: "headache"
- Input: "fever aur cough" → is_medical: true, detected_symptoms: "fever and cough"
"""

    validation_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[{"role": "user", "content": validation_prompt}]
    )

    validation_raw = validation_response.choices[0].message.content
    validation_clean = re.sub(r"```json|```", "", validation_raw).strip()

    try:
        validation = json.loads(validation_clean)
    except json.JSONDecodeError:
        # If parsing fails, assume it's medical and proceed
        validation = {"is_medical": True, "detected_symptoms": text, "response_message": None}

    # If not medical input, return friendly response
    if not validation.get("is_medical", True):
        return {
            "is_medical_input": False,
            "message": validation.get("response_message", "Please tell me about your symptoms so I can help you."),
            "conditions": [],
            "home_care_tips": [],
            "red_flags": [],
            "disclaimer": "Please describe your symptoms (e.g., headache, fever, pain, etc.) for analysis."
        }

    # Proceed with medical analysis
    actual_symptoms = validation.get("detected_symptoms") or text

    prompt = f"""You are a medical AI assistant for Pakistani users. The user may write in English or Roman Urdu.

User input: "{text}"
Detected symptoms: "{actual_symptoms}"

IMPORTANT: Only analyze the actual symptoms mentioned. Do NOT invent or hallucinate symptoms that weren't mentioned.

Respond in JSON only. No extra text, no markdown, no explanation outside the JSON.

{{
  "is_medical_input": true,
  "message": null,
  "conditions": [
    {{
      "name": "Most likely condition based ONLY on the symptoms mentioned",
      "confidence": 85,
      "severity": "low" or "medium" or "high",
      "description": "Brief description of the condition"
    }},
    {{
      "name": "Second possibility if symptoms are unclear",
      "confidence": 65,
      "severity": "low" or "medium" or "high",
      "description": "Brief description"
    }},
    {{
      "name": "Third possibility or differential diagnosis",
      "confidence": 25,
      "severity": "low" or "medium" or "high",
      "description": "Brief description"
    }}
  ],
  "home_care_tips": [
    "Practical tip 1 relevant to the symptoms",
    "Practical tip 2",
    "Practical tip 3",
    "Practical tip 4",
    "Practical tip 5"
  ],
  "red_flags": [
    "Red flag symptom 1 - when to seek immediate care",
    "Red flag symptom 2",
    "Red flag symptom 3",
    "Red flag symptom 4"
  ],
  "disclaimer": "This is not a substitute for professional medical advice."
}}

STRICT RULES:
1. ONLY base your analysis on symptoms actually mentioned by the user
2. If symptoms are vague, acknowledge uncertainty and give broader possibilities
3. Do NOT diagnose serious mental health conditions (anxiety disorder, depression) unless specific psychological symptoms are described
4. For simple greetings or non-medical input, this function should not be called - but if it is, return low-confidence general wellness advice only
5. Confidence scores must reflect actual certainty - low for vague symptoms, higher for specific symptom clusters
6. Condition names must always be in English
7. Descriptions, tips, red_flags should be in same language as user input (English or Roman Urdu)"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)
