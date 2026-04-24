from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
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

class Input(BaseModel):
    text: str

class MedicationsInput(BaseModel):
    medicines: list[str]

@app.get("/")
def root():
    return {"message": "HealthAI Pakistan API is running"}

@app.post("/symptoms")
def analyze_symptoms(input_data: Input):
    """Analyze symptoms and provide medical insights"""
    try:
        result = check_symptoms(input_data.text, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/medications")
def check_medication_interactions(input_data: MedicationsInput):
    """Check for drug interactions"""
    try:
        result = check_medications(input_data.medicines, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/alternatives")
def find_generic_alternatives(input_data: MedicationsInput):
    """Find generic alternatives for medicines"""
    try:
        # Use the same medication checker for alternatives
        result = check_medications(input_data.medicines, GROQ_API_KEY, find_alternatives=True)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/specialist")
def recommend_doctor(input_data: Input):
    """Recommend appropriate specialist"""
    try:
        result = recommend_specialist(input_data.text, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/go-or-stay")
def hospital_decision(input_data: Input):
    """Decide whether to go to hospital or stay home"""
    try:
        result = check_go_or_stay(input_data.text, GROQ_API_KEY)
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
