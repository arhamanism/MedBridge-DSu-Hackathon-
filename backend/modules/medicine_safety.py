import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def check_medications(medicines: list[str]) -> dict:
    # First check if the medicines list contains actual medicine names
    medicine_keywords = [
        'panadol', 'paracetamol', 'acetaminophen', 'brufen', 'ibuprofen', 'aspirin',
        'disprin', 'cataflam', 'diclofenac', 'voltaren', 'arcoxia', 'etoricoxib',
        'calpol', 'tylenol', 'advil', 'motrin', 'aleve', 'naproxen', 'mefenamic',
        'ponstan', 'augmentin', 'amoxicillin', 'azithromycin', 'zithromax',
        'ciprofloxacin', 'cipro', 'levofloxacin', 'ofloxacin', 'flagyl',
        'metronidazole', 'clarithromycin', 'erythromycin', 'doxycycline',
        'ampicillin', 'penicillin', 'cephalexin', 'clindamycin', 'tetracycline',
        'gaviscon', 'digene', 'omeprazole', 'nexium', 'pantoprazole', 'ranitidine',
        'zantac', 'antacid', 'lansoprazole', 'esomeprazole', 'rabeprazole',
        'metformin', 'glucophage', 'insulin', 'glyburide', 'glipizide',
        'actos', 'pioglitazone', 'januvia', 'sitagliptin', 'farxiga',
        'losartan', 'cozaar', 'valsartan', 'diovan', 'lisinopril', 'zestril',
        'atenolol', 'tenormin', 'metoprolol', 'lopressor', 'propranolol',
        'amlodipine', 'norvasc', 'nifedipine', 'adalat', 'diltiazem',
        'atorvastatin', 'lipitor', 'simvastatin', 'zocor', 'rosuvastatin',
        'crestor', 'hydrochlorothiazide', 'furosemide', 'lasix', 'spironolactone',
        'warfarin', 'coumadin', 'clopidogrel', 'plavix', 'heparin',
        'vitamin', 'supplement', 'calcium', 'iron', 'folic', 'zinc',
        'cough', 'syrup', 'benadryl', 'diphenhydramine', 'cetirizine',
        'zyrtec', 'loratadine', 'claritin', 'fexofenadine', 'allegra',
        'salbutamol', 'ventolin', 'seretide', 'symbicort', 'pulmicort'
    ]
    
    # Check if any medicine name contains actual medicine keywords
    has_medicines = False
    for med in medicines:
        med_lower = med.lower().strip()
        if len(med_lower) < 2 or med_lower in ['j', 'a', 'x', 'z', 'hello', 'hi']:
            continue
        # Check if it contains medicine keywords
        if any(keyword in med_lower for keyword in medicine_keywords):
            has_medicines = True
            break
        # Also accept longer inputs that might be medicine names
        elif len(med_lower) >= 3:
            has_medicines = True
            break
    
    if not has_medicines:
        return {
            "is_safe": True,
            "interactions": [],
            "summary": "No valid medicines detected",
            "disclaimer": "Please enter actual medicine names to check for interactions."
        }
    
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
