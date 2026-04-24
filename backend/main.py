from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional


from modules.go_or_stay import check_go_or_stay
from modules.specialist_recommender import recommend_specialist
from modules.symptom_checker import (
    check_symptoms,
    get_supported_languages,
    get_red_flags_info,
    SymptomInput,
    SymptomAnalysis
)


app = FastAPI(title="MedBridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    text: str


@app.get("/")
def root():
    return {"message": "MedBridge API is running"}


# =====================
# Go or Stay Endpoint
# =====================
@app.post("/go-or-stay")
async def go_or_stay(data: Input):
    if not data.text:
        raise HTTPException(status_code=400, detail="No input provided")
    return check_go_or_stay(data.text)


# =====================
# Specialist Recommender Endpoint
# =====================
@app.post("/specialist")
async def specialist(data: Input):
    if not data.text:
        raise HTTPException(status_code=400, detail="No input provided")
    return recommend_specialist(data.text)


# =====================
# Symptom Checker Endpoints
# =====================
@app.post("/check-symptoms", response_model=SymptomAnalysis)
async def symptoms_checker(input_data: SymptomInput):
    """
    Analyze symptoms and return possible conditions with recommendations.
    
    Supports input in:
    - English
    - Roman Urdu (e.g., "mujhe bukhaar aur sar dard ho raha hai")
    - Mixed language
    
    Returns:
    - Interpreted symptoms
    - Possible conditions with confidence levels
    - Red flags requiring immediate attention
    - Home care recommendations for mild cases
    """
    if not input_data.symptoms:
        raise HTTPException(status_code=400, detail="No symptoms provided")
    
    try:
        return check_symptoms(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/supported-languages")
async def supported_languages():
    """Get list of supported input languages for symptom checker"""
    return get_supported_languages()


@app.get("/red-flags-info")
async def red_flags_info():
    """Get information about red flag symptoms"""
    return get_red_flags_info()
