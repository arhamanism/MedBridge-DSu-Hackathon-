from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from faster_whisper import WhisperModel
import tempfile
import os
import requests
from dotenv import load_dotenv

load_dotenv()

from modules.hospital_decision import check_go_or_stay
from modules.doctor_finder import recommend_specialist
from modules.symptom_analyzer import check_symptoms
from modules.medicine_safety import check_medications

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


# Load Whisper model once at startup
print("Loading Whisper model...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Whisper ready.")


app = FastAPI(title="MedBridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    text: str


class MedicationsInput(BaseModel):
    medicines: list[str]


@app.get("/")
def root():
    return {"message": "MedBridge API is running"}




@app.post("/go-or-stay")
async def go_or_stay(data: Input):
    if not data.text:
        raise HTTPException(status_code=400, detail="No input provided")
    return check_go_or_stay(data.text)




@app.post("/specialist")
async def specialist(data: Input):
    if not data.text:
        raise HTTPException(status_code=400, detail="No input provided")
    return recommend_specialist(data.text)


@app.post("/symptoms")
async def symptoms(data: Input):
    if not data.text:
        raise HTTPException(status_code=400, detail="No input provided")
    return check_symptoms(data.text)


@app.post("/medications")
async def medications(data: MedicationsInput):
    if not data.medicines or len(data.medicines) < 1:
        raise HTTPException(status_code=400, detail="At least one medicine required")
    return check_medications(data.medicines)


def normalize_to_roman(text: str, detected_lang: str) -> str:
    """Convert Hindi/Urdu script to Roman Urdu, keep English as is"""
    if detected_lang == "en":
        return text

    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY not found. Returning un-normalized text.")
        return text

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": """Normalize text for a Pakistani medical app.
- Hindi/Urdu script (Devanagari) → Roman Urdu (WhatsApp style)
- English → unchanged
- Mixed → keep English, convert Hindi/Urdu parts only
Return only the result text in Roman Urdu or English."""
                },
                {"role": "user", "content": text}
            ]
        }
    )

    data = response.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"].strip()
    else:
        print("Error from Groq API:", data)
        return text


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    # Save uploaded audio temporarily
    suffix = os.path.splitext(audio.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(tmp_path, beam_size=5)
        full_text = "".join(s.text + " " for s in segments).strip()
    finally:
        os.unlink(tmp_path)

    # Normalize Hindi/Urdu script to Roman Urdu
    normalized = normalize_to_roman(full_text, info.language)

    return {
        "transcript": normalized,
        "raw": full_text,
        "detected_language": info.language,
        "confidence": round(info.language_probability, 2)
    }


@app.post("/extract-medicines")
async def extract_medicines(image: UploadFile = File(...)):
    """Extract medicine names from prescription image using AI"""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    # Read image bytes
    image_bytes = await image.read()
    import base64
    image_b64 = base64.b64encode(image_bytes).decode()

    # Call Groq API with vision
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Extract all medicine names from this prescription image.
Return ONLY a JSON object in this format:
{
  "medicines": ["Medicine1", "Medicine2", "Medicine3"]
}
If no medicines found, return {"medicines": []}.
Extract only the medicine names, not dosages or instructions."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
    )

    data = response.json()
    if "choices" not in data:
        print("Groq API error:", data)
        raise HTTPException(status_code=500, detail="Failed to process image")

    content = data["choices"][0]["message"]["content"]

    # Parse JSON from response
    import json
    import re
    try:
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            # Try to find raw JSON object
            json_match = re.search(r'(\{[\s\S]*\})', content)
            if json_match:
                content = json_match.group(1)

        result = json.loads(content)
        return {"medicines": result.get("medicines", [])}
    except json.JSONDecodeError:
        # Fallback: try to extract medicine names manually
        print("Failed to parse JSON, raw content:", content)
        return {"medicines": []}


@app.post("/alternatives")
async def find_alternatives(data: MedicationsInput):
    """Find generic alternatives for given medicines with Pakistani pricing"""
    if not data.medicines or len(data.medicines) < 1:
        raise HTTPException(status_code=400, detail="At least one medicine required")

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    medicines_text = ", ".join(data.medicines)

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a Pakistani pharmacy expert. Find ONLY verified generic alternatives.

CRITICAL RULES - FOLLOW STRICTLY:

1. ONLY suggest alternatives you are 100% certain exist in Pakistan
2. If unsure about a brand name, DO NOT suggest it - skip that medicine
3. Prefer well-known brands: Panadol, Calpol, Brufen, Voveran, Ponstan, Disprin, etc.
4. If the medicine is already generic (Paracetamol, Ibuprofen, Aspirin), return empty list
5. Never invent brand names - only use verified real brands

VERIFIED COMMON PAKISTANI GENERICS (use only these):
- Pain/NSAIDs: Voveran (Diclofenac), Brufen (Ibuprofen), Ponstan (Mefenamic Acid), Disprin (Aspirin)
- Fever: Calpol (Paracetamol), Panadol (Paracetamol)
- Antibiotics: Augmentin (Amoxicillin+Clav), Flagyl (Metronidazole)
- Stomach: Risek (Omeprazole), Motilium (Domperidone)
- Vitamins: Jointace, Neurobion, etc.

Return ONLY JSON:
{
  "alternatives": [
    {
      "original": "Brand name",
      "original_ingredient": "Active ingredient",
      "generic": "Verified cheaper brand",
      "savings_percent": 20-70,
      "original_price": "Rs. XXX",
      "generic_price": "Rs. XXX"
    }
  ],
  "total_savings": "Rs. XXX",
  "disclaimer": "IMPORTANT: All brand names and prices are AI-generated for demonstration. ALWAYS verify with a licensed pharmacist before purchasing. Only buy from registered pharmacies."
}

If uncertain about alternatives, return: {"alternatives": [], "total_savings": "Rs. 0", "disclaimer": "No verified alternatives found. Consult a pharmacist for generic options."}"""
                },
                {
                    "role": "user",
                    "content": f"Find generic alternatives for these medicines. Only include if there are real savings: {medicines_text}"
                }
            ],
            "max_tokens": 1500
        }
    )

    data_resp = response.json()
    if "choices" not in data_resp:
        print("Groq API error:", data_resp)
        raise HTTPException(status_code=500, detail="Failed to find alternatives")

    content = data_resp["choices"][0]["message"]["content"]

    # Parse JSON
    import json
    import re
    try:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            json_match = re.search(r'(\{[\s\S]*\})', content)
            if json_match:
                content = json_match.group(1)

        result = json.loads(content)

        # Filter to only keep real alternatives with actual savings
        valid_alternatives = []
        for alt in result.get("alternatives", []):
            original = alt.get("original", "").lower().strip()
            generic = alt.get("generic", "").lower().strip()
            savings = alt.get("savings_percent", 0)

            # Skip if same name
            if original == generic:
                continue

            # Skip if no real savings (savings <= 0 or generic same/expensive)
            if savings <= 0:
                continue

            # Skip if suggesting to switch to ingredient name (not a brand)
            ingredient = alt.get("original_ingredient", "").lower().strip()
            if generic == ingredient:
                continue

            # Skip nonsense text
            if "already" in generic or "generic" in generic or "no cheaper" in generic:
                continue

            valid_alternatives.append(alt)

        result["alternatives"] = valid_alternatives

        # If no valid alternatives, update message
        if len(valid_alternatives) == 0:
            result["total_savings"] = "Rs. 0"
            result["disclaimer"] = "No cheaper alternatives found. Your medicines are already cost-effective or no generic options exist."

        return result

    except json.JSONDecodeError:
        print("Failed to parse alternatives JSON:", content)
        return {
            "alternatives": [],
            "total_savings": "Rs. 0",
            "disclaimer": "Could not find alternatives. Your medicines may already be generic options."
        }
