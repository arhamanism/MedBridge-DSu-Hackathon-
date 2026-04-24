from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from dotenv import load_dotenv

load_dotenv()

from modules.hospital_decision import check_go_or_stay
from modules.doctor_finder import recommend_specialist
from modules.symptom_analyzer import check_symptoms
from modules.medicine_safety import check_medications

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

app = FastAPI(title="HealthAI Pakistan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"message": "HealthAI Pakistan API is running"}

@app.post("/symptoms")
def analyze_symptoms(data: dict):
    """Analyze symptoms and provide medical insights"""
    text = data.get("text", "")
    if not text:
        return {"error": "Text is required"}
    
    try:
        result = check_symptoms(text, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/medications")
def check_medicine_interactions(data: dict):
    """Check for drug interactions"""
    medicines = data.get("medicines", [])
    if not medicines:
        return {"error": "Medicines list is required"}
    
    try:
        result = check_medications(medicines, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/alternatives")
def find_generic_alternatives(data: dict):
    """Find generic alternatives for medicines"""
    medicines = data.get("medicines", [])
    if not medicines:
        return {"error": "Medicines list is required"}
    
    try:
        result = check_medications(medicines, GROQ_API_KEY, find_alternatives=True)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/specialist")
def recommend_doctors(data: dict):
    """Recommend specialists based on symptoms"""
    text = data.get("text", "")
    if not text:
        return {"error": "Text is required"}
    
    try:
        result = recommend_specialist(text, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/go-or-stay")
def hospital_decision(data: dict):
    """Decide whether to go to hospital or stay home"""
    text = data.get("text", "")
    if not text:
        return {"error": "Text is required"}
    
    try:
        result = check_go_or_stay(text, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/transcribe")
def transcribe_audio_placeholder(data: dict):
    """Placeholder for transcription - voice input disabled for deployment"""
    return {
        "transcript": "Voice input disabled in deployment. Please use text input.",
        "normalized": "Voice input disabled in deployment. Please use text input.",
        "has_symptoms": False,
        "warning": "Voice input is disabled in deployment. Please type your symptoms."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
