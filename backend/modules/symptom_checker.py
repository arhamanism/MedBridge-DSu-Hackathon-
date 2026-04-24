import os
import json
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI

# Initialize Groq client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("XAI_API_KEY", "")
)


class SymptomInput(BaseModel):
    """Input model for symptom description"""
    symptoms: str = Field(
        ...,
        description="Description of symptoms in English or Roman Urdu",
        min_length=3,
        max_length=2000,
        examples=[
            "mujhe bukhaar aur sar dard ho raha hai",
            "I have a fever and headache",
            "pet mein dard aur ulti aa rahi hai"
        ]
    )
    age: Optional[int] = Field(
        None,
        description="Patient age in years",
        ge=0,
        le=150
    )
    gender: Optional[str] = Field(
        None,
        description="Patient gender",
        pattern="^(male|female|other)$"
    )


class Condition(BaseModel):
    """A possible medical condition"""
    name: str = Field(..., description="Name of the condition")
    confidence: float = Field(
        ...,
        description="Confidence level as percentage (0-100)",
        ge=0,
        le=100
    )
    description: str = Field(..., description="Brief description of the condition")
    severity: str = Field(
        ...,
        description="Severity level",
        pattern="^(mild|moderate|severe|critical)$"
    )


class RedFlag(BaseModel):
    """A red flag symptom requiring immediate attention"""
    symptom: str = Field(..., description="The concerning symptom")
    reason: str = Field(..., description="Why this requires immediate attention")
    action: str = Field(..., description="Recommended immediate action")


class HomeCareStep(BaseModel):
    """A home care recommendation"""
    step: str = Field(..., description="Description of the home care step")
    category: str = Field(
        ...,
        description="Category of care",
        pattern="^(rest|hydration|medication|diet|monitoring|lifestyle)$"
    )
    important: bool = Field(False, description="Whether this is particularly important")


class SymptomAnalysis(BaseModel):
    """Complete symptom analysis response"""
    original_input: str = Field(..., description="The original symptom description")
    interpreted_symptoms: list[str] = Field(
        ...,
        description="List of interpreted symptoms from the input"
    )
    language_detected: str = Field(
        ...,
        description="Detected language of input"
    )
    possible_conditions: list[Condition] = Field(
        ...,
        description="List of possible conditions with confidence levels"
    )
    red_flags: list[RedFlag] = Field(
        default_factory=list,
        description="Red flag symptoms requiring immediate hospital attention"
    )
    requires_immediate_attention: bool = Field(
        False,
        description="Whether the patient should seek immediate medical care"
    )
    home_care_steps: list[HomeCareStep] = Field(
        default_factory=list,
        description="Safe home care steps for mild cases"
    )
    disclaimer: str = Field(
        default="This is an AI-based preliminary assessment and should not replace professional medical advice. If symptoms persist or worsen, please consult a healthcare provider immediately.",
        description="Medical disclaimer"
    )


SYMPTOM_ANALYSIS_PROMPT = """You are a medical symptom analysis AI assistant. Your role is to analyze symptoms described by users and provide helpful preliminary assessments.

IMPORTANT: You must understand symptoms described in:
- English
- Roman Urdu (Urdu written in English letters, e.g., "bukhaar" means fever, "sar dard" means headache)
- Mixed language input
- Various spelling variations

CRITICAL LANGUAGE REQUIREMENT:
- You MUST respond in the SAME LANGUAGE as the user's input.
- If the user writes in Roman Urdu, respond entirely in Roman Urdu.
- If the user writes in English, respond entirely in English.
- If the user uses mixed language, respond in the dominant language of their input.
- All field values in your JSON response (descriptions, steps, reasons, actions, condition names, etc.) must be in the detected language.

When analyzing symptoms, you must:
1. Correctly interpret the symptoms regardless of language or spelling
2. Identify possible medical conditions with confidence levels
3. Flag any RED FLAGS that require IMMEDIATE hospital attention
4. Provide safe home care recommendations for mild cases
5. Respond in the SAME LANGUAGE as the user input

RED FLAG symptoms that require IMMEDIATE medical attention include:
- Chest pain or pressure
- Difficulty breathing or shortness of breath
- Sudden severe headache ("worst headache of life")
- Signs of stroke (face drooping, arm weakness, speech difficulty)
- Severe abdominal pain
- High fever (>104°F/40°C) especially in children
- Severe dehydration (no urination, extreme thirst)
- Confusion or altered consciousness
- Severe allergic reactions
- Uncontrolled bleeding
- Suicidal thoughts

Common Roman Urdu medical terms:
- bukhaar/bukhar = fever
- sar dard/sir dard = headache
- pet dard = stomach ache
- ulti = vomiting
- dast = diarrhea
- khansi = cough
- nazla/zukam = cold
- gala kharab = sore throat
- chakkar = dizziness
- kamzori = weakness
- thakan = fatigue
- jor dard = joint pain
- kamar dard = back pain
- seena dard = chest pain
- sans lene mein taklif = difficulty breathing

Analyze the following symptoms and provide a JSON response with the exact structure specified."""


def check_symptoms(input_data: SymptomInput) -> dict:
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
    
    user_message = f"""Analyze these symptoms:

Symptoms: {input_data.symptoms}
{f"Age: {input_data.age} years" if input_data.age else ""}
{f"Gender: {input_data.gender}" if input_data.gender else ""}

IMPORTANT: Respond in the SAME LANGUAGE as the symptoms input above. If the input is in Roman Urdu, write ALL your response content (descriptions, names, steps, reasons, actions) in Roman Urdu. If the input is in English, respond in English.

Provide your analysis in the following JSON format:
{{
    "original_input": "<the exact symptom text provided>",
    "interpreted_symptoms": ["<symptom1>", "<symptom2>", ...],
    "language_detected": "<English/Roman Urdu/Mixed>",
    "possible_conditions": [
        {{
            "name": "<condition name>",
            "confidence": <0-100>,
            "description": "<brief description>",
            "severity": "<mild/moderate/severe/critical>"
        }}
    ],
    "red_flags": [
        {{
            "symptom": "<concerning symptom>",
            "reason": "<why it's concerning>",
            "action": "<what to do immediately>"
        }}
    ],
    "requires_immediate_attention": <true/false>,
    "home_care_steps": [
        {{
            "step": "<what to do>",
            "category": "<rest/hydration/medication/diet/monitoring/lifestyle>",
            "important": <true/false>
        }}
    ]
}}

Be thorough but concise. Include 2-5 possible conditions ordered by likelihood. Only include red_flags if truly concerning symptoms are present.

Remember: ALL text content in your response must be in the same language as the user's input. For Roman Urdu input, write everything in Roman Urdu (e.g., "bukhaar" not "fever", "aaram karein" not "take rest")."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYMPTOM_ANALYSIS_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure all required fields are present with defaults
        analysis = SymptomAnalysis(
            original_input=result.get("original_input", input_data.symptoms),
            interpreted_symptoms=result.get("interpreted_symptoms", []),
            language_detected=result.get("language_detected", "Unknown"),
            possible_conditions=[
                Condition(**cond) for cond in result.get("possible_conditions", [])
            ],
            red_flags=[
                RedFlag(**flag) for flag in result.get("red_flags", [])
            ],
            requires_immediate_attention=result.get("requires_immediate_attention", False),
            home_care_steps=[
                HomeCareStep(**step) for step in result.get("home_care_steps", [])
            ]
        )
        
        return analysis.model_dump()
        
    except Exception as e:
        raise Exception(f"Error analyzing symptoms: {str(e)}")


def get_supported_languages() -> dict:
    """Get list of supported input languages"""
    return {
        "languages": [
            {
                "code": "en",
                "name": "English",
                "example": "I have a fever and headache"
            },
            {
                "code": "ur-roman",
                "name": "Roman Urdu",
                "example": "mujhe bukhaar aur sar dard ho raha hai"
            },
            {
                "code": "mixed",
                "name": "Mixed (English + Roman Urdu)",
                "example": "I have bukhaar and sar dard"
            }
        ],
        "common_terms": {
            "fever": ["bukhaar", "bukhar", "fever"],
            "headache": ["sar dard", "sir dard", "headache"],
            "stomach_ache": ["pet dard", "stomach ache", "stomach pain"],
            "vomiting": ["ulti", "vomiting", "qai"],
            "diarrhea": ["dast", "diarrhea", "loose motions"],
            "cough": ["khansi", "cough"],
            "cold": ["nazla", "zukam", "cold"],
            "sore_throat": ["gala kharab", "sore throat"],
            "dizziness": ["chakkar", "dizziness"],
            "weakness": ["kamzori", "weakness"],
            "fatigue": ["thakan", "fatigue", "tiredness"],
            "joint_pain": ["jor dard", "joint pain"],
            "back_pain": ["kamar dard", "back pain"],
            "chest_pain": ["seena dard", "chest pain"],
            "breathing_difficulty": ["sans lene mein taklif", "difficulty breathing"]
        }
    }


def get_red_flags_info() -> dict:
    """Get information about red flag symptoms"""
    return {
        "title": "Red Flag Symptoms Requiring Immediate Medical Attention",
        "description": "If you experience any of these symptoms, seek emergency medical care immediately.",
        "red_flags": [
            {
                "symptom": "Chest pain or pressure",
                "urdu": "Seena mein dard ya dabao",
                "urgency": "critical"
            },
            {
                "symptom": "Difficulty breathing",
                "urdu": "Sans lene mein mushkil",
                "urgency": "critical"
            },
            {
                "symptom": "Sudden severe headache",
                "urdu": "Achanak shadeed sar dard",
                "urgency": "critical"
            },
            {
                "symptom": "Signs of stroke (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call emergency)",
                "urdu": "Stroke ki alamaat",
                "urgency": "critical"
            },
            {
                "symptom": "Severe abdominal pain",
                "urdu": "Shadeed pet dard",
                "urgency": "high"
            },
            {
                "symptom": "High fever (>104°F/40°C)",
                "urdu": "Tez bukhaar",
                "urgency": "high"
            },
            {
                "symptom": "Severe dehydration",
                "urdu": "Shadeed pani ki kami",
                "urgency": "high"
            },
            {
                "symptom": "Confusion or altered consciousness",
                "urdu": "Confusion ya hosh mein kami",
                "urgency": "critical"
            },
            {
                "symptom": "Severe allergic reaction",
                "urdu": "Shadeed allergy ka reaction",
                "urgency": "critical"
            },
            {
                "symptom": "Uncontrolled bleeding",
                "urdu": "Khoon band na hona",
                "urgency": "critical"
            }
        ],
        "emergency_numbers": {
            "pakistan": "1122 (Rescue), 115 (Edhi)",
            "usa": "911",
            "uk": "999",
            "general": "Contact your local emergency services"
        }
    }
