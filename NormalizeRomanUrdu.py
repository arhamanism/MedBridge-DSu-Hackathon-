import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(
    title="MedBridge NLP API",
    description="Medical language normalization for Roman Urdu / Urdu / English",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Groq Configuration ----------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a medical language normalization assistant for Pakistan.
Your job is to process user input that may be in:
- Roman Urdu (with variations like "soraha", "suraha", "rha", "hy")
- Urdu script
- English
- Mixed language

Tasks:
1. Detect the language.
2. Normalize spelling variations into a "Standardized Roman Urdu" format (WhatsApp style but consistent).
3. Translate into clear medical English.
4. Extract ONLY explicitly mentioned symptoms.

STANDARDIZATION RULES (Roman Urdu):
- Verbs: "ho raha" (not "horaha"), "hoon" (not "hon/hun"), "hai" (not "hy/he"), "raha" (not "rha").
- Common Terms: "bukhaar" (fever), "dard" (pain), "khansi" (cough), "pait" (stomach), "bohat" (very).
- Pronouns: "mujhe" (not "mjhe"), "mere" (not "mre").
- Normalize vowel variations: "soraha/suraha" -> "so raha".

FEW-SHOT EXAMPLES:
Input: "mujhe teen din se tez bukhaar hai"
Output: {
  "language": "Roman Urdu",
  "normalized_text": "Mujhe teen din se tez bukhaar hai",
  "english_translation": "I have had a high fever for three days",
  "symptoms": [{"symptom": "fever", "severity_hint": "severe", "original_term": "tez bukhaar"}]
}

Input: "sir mien drd horha hy"
Output: {
  "language": "Roman Urdu",
  "normalized_text": "Sir mein dard ho raha hai",
  "english_translation": "I have a headache",
  "symptoms": [{"symptom": "headache", "severity_hint": "unspecified", "original_term": "drd"}]
}

STRICT RULES:
- Do NOT add or assume symptoms.
- Keep output medically accurate.
- If no symptoms found, return empty list.
- Return symptom severity hints if words like "tez", "shadeed", "bohat", "kafi" appear.

Output MUST be valid JSON only matching this exact schema:
{
  "language": "Roman Urdu | Urdu | English | Mixed",
  "normalized_text": "standardized Roman Urdu or cleaned English version",
  "english_translation": "clear medical English translation",
  "symptoms": [
    {
      "symptom": "symptom name in medical English",
      "severity_hint": "mild | moderate | severe | unspecified",
      "original_term": "exact word(s) user used"
    }
  ]
}"""


# ---------- request / response models ----------

class NormalizeRequest(BaseModel):
    text: str

    class Config:
        json_schema_extra = {
            "example": {
                "text": "mujhe teen din se tez bukhaar hai aur sar mein bohat dard ho raha hai"
            }
        }

class Symptom(BaseModel):
    symptom: str
    severity_hint: str
    original_term: str

class NormalizeResponse(BaseModel):
    language: str
    normalized_text: str
    english_translation: str
    symptoms: list[Symptom]


# ---------- Normalization Utils ----------

def preprocess_text(text: str) -> str:
    """
    Basic regex-based normalization for common Roman Urdu variations.
    This helps the LLM by providing a slightly cleaner starting point.
    """
    import re
    
    # Lowercase for easier matching
    text = text.lower()
    
    mappings = {
        r"\bmjhe\b": "mujhe",
        r"\bmre\b": "mere",
        r"\bdrd\b": "dard",
        r"\bhy\b": "hai",
        r"\bhe\b": "hai",
        r"\brha\b": "raha",
        r"\bbht\b": "bohat",
        r"\bboht\b": "bohat",
        r"\bbkar\b": "bukhaar",
        r"\bbukhar\b": "bukhaar",
        r"\bpet\b": "pait",
        r"\bpayt\b": "pait",
        r"\bkansi\b": "khansi",
        r"\bkhansi\b": "khansi",
        r"\bhon\b": "hoon",
        r"\bhun\b": "hoon",
        r"\bsoraha\b": "so raha",
        r"\bsuraha\b": "so raha",
        r"\bhoraha\b": "ho raha",
    }
    
    for pattern, replacement in mappings.items():
        text = re.sub(pattern, replacement, text)
        
    return text.strip()

# ---------- routes ----------

@app.get("/", summary="Root Endpoint")
async def root():
    return {
        "message": "MedBridge NLP API is running with Groq!", 
        "docs_url": "Go to /docs to test the API"
    }

@app.post("/normalize", response_model=NormalizeResponse, summary="Normalize medical text")
async def normalize(body: NormalizeRequest):
    if not body.text.strip():
        raise HTTPException(status_code=422, detail="Input text cannot be empty.")

    # Pre-process the text for common variations
    cleaned_text = preprocess_text(body.text)

    try:
        # Call the Groq API via requests
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": cleaned_text}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Groq API Error: {response.text}")
            
        data = response.json()
        raw = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network or API Error: {str(e)}")

    try:
        # Groq guarantees valid JSON because of response_format
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Model returned unparseable output: {raw[:200]}",
        ) from exc

    # Ensure symptoms list always contains dicts with the required keys
    symptoms = []
    for s in parsed.get("symptoms", []):
        symptoms.append(
            Symptom(
                symptom=s.get("symptom", ""),
                severity_hint=s.get("severity_hint", "unspecified"),
                original_term=s.get("original_term", ""),
            )
        )

    return NormalizeResponse(
        language=parsed.get("language", "Unknown"),
        normalized_text=parsed.get("normalized_text", body.text),
        english_translation=parsed.get("english_translation", ""),
        symptoms=symptoms,
    )

@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "MedBridge NLP (Groq)"}