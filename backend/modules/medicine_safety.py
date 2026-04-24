import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def check_medications(medicines: list[str]) -> dict:
    medicines_str = ", ".join(medicines)

    prompt = f"""You are a medical AI assistant for Pakistani users.

Check for interactions between these medicines: {medicines_str}

Respond in JSON only. No extra text, no markdown, no explanation outside the JSON.

{{
  "is_safe": true or false,
  "interactions": [
    {{
      "drug1": "Medicine name 1",
      "drug2": "Medicine name 2",
      "risk": "low" or "medium" or "high",
      "description": "Description of the interaction"
    }}
  ],
  "summary": "Brief summary of overall safety",
  "disclaimer": "This is not a substitute for professional medical advice. Always consult a pharmacist or doctor."
}}

Rules:
- is_safe is false if ANY interaction has risk "high"
- Provide all interactions found between the given medicines
- If no interactions found, return empty interactions array and is_safe: true
- Risk levels: "high" = dangerous, do not mix; "medium" = caution, consult doctor; "low" = minor, can usually be taken together
- Be specific about Pakistani brand names (Panadol, Brufen, Calpol, etc.) and their generic equivalents
- Return response in English regardless of input"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)
