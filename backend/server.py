import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import tempfile
import os
import requests
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# load once at startup
print("Loading Whisper model...")
model = WhisperModel("small", device="cuda", compute_type="float16")
print("Whisper ready.")

def normalize_to_roman(text: str, detected_lang: str) -> str:
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
- Urdu/Hindi script → Roman Urdu (WhatsApp style)
- English → unchanged
- Mixed → keep English, convert Urdu parts only
Return only the result text."""
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
        # Fallback to original text if API fails (e.g. rate limit, invalid key)
        return text

@app.get("/")
def root():
    return {"status": "MedBridge Voice API running"}

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    # save uploaded audio temporarily
    suffix = os.path.splitext(audio.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(tmp_path, beam_size=5)
        full_text = "".join(s.text + " " for s in segments).strip()
    finally:
        os.unlink(tmp_path)

    normalized = normalize_to_roman(full_text, info.language)

    return {
        "transcript": normalized,
        "raw": full_text,
        "detected_language": info.language,
        "confidence": round(info.language_probability, 2)
    }

@app.post("/prescription")
async def analyze_prescription(image: UploadFile = File(...)):
    # read image and convert to base64
    image_data = await image.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    
    # Step 1 — extract medicine names using Groq Vision
    extract_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.2-11b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a medical prescription. \nExtract all medicine names, dosages, and frequency.\nIf handwriting is unclear make your best guess.\nReturn as JSON only:\n{\n  \"medicines\": [\n    {\"name\": \"medicine name\", \"dosage\": \"500mg\", \"frequency\": \"twice daily\", \"confidence\": \"high/medium/low\"}\n  ],\n  \"doctor_notes\": \"any other instructions visible\"\n}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
    )
    
    extract_data = extract_response.json()
    if "choices" not in extract_data:
        return {"error": "Failed to extract text from image", "details": extract_data}

    extracted = extract_data["choices"][0]["message"]["content"]
    
    # Step 2 — find generic alternatives
    alternatives_response = requests.post(
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
                    "content": "You are a Pakistani pharmacist assistant.\nFor each medicine given, provide:\n1. Generic formula/salt name\n2. Cheaper local alternatives available in Pakistan\n3. Estimated price of branded vs generic in PKR\n4. Whether substitution needs doctor approval\n\nBe specific to Pakistan market. Format as clean readable text."
                },
                {
                    "role": "user",
                    "content": f"Find generic alternatives for these medicines: {extracted}"
                }
            ]
        }
    )
    
    alternatives_data = alternatives_response.json()
    if "choices" not in alternatives_data:
        alternatives = "Could not fetch alternatives at this time."
    else:
        alternatives = alternatives_data["choices"][0]["message"]["content"]
    
    return {
        "extracted_medicines": extracted,
        "generic_alternatives": alternatives
    }

