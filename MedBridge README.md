# **MedBridge NLP Module**

Medical language normalization for Roman Urdu / Urdu / English. Powered by Groq and Llama 3\.

## **Setup**

First, make sure to install all the required dependencies from your requirements.txt file.

pip install \-r requirements.txt

Set your Groq API key in your terminal:

\# For Windows Command Prompt:  
set GROQ\_API\_KEY=gsk\_...

\# For Windows PowerShell:  
$env:GROQ\_API\_KEY="gsk\_..."

\# For Mac/Linux:  
export GROQ\_API\_KEY=gsk\_...

Start the local server:

python \-m uvicorn main:app \--reload

## **Endpoint**

### **POST /normalize**

**Request**

{ "text": "mujhe teen din se tez bukhaar hai aur sar mein bohat dard ho raha hai" }

**Response**

{  
  "language": "Roman Urdu",  
  "normalized\_text": "Mujhe teen din se tez bukhar hai aur sar mein bohat dard ho raha hai",  
  "english\_translation": "I have had a high fever for three days and a very bad headache",  
  "symptoms": \[  
    { "symptom": "fever", "severity\_hint": "severe", "original\_term": "tez bukhaar" },  
    { "symptom": "headache", "severity\_hint": "severe", "original\_term": "bohat dard" }  
  \]  
}

### **GET /health**

Returns { "status": "ok", "service": "MedBridge NLP (Groq)" }.

## **Severity mapping**

| Roman Urdu word | Maps to |
| :---- | :---- |
| tez | severe |
| shadeed | severe |
| bohat / kafi | moderate |
| zyaada | moderate |
| thora / halka | mild |
| (none) | unspecified |

## **Docs**

Auto-generated Swagger UI available at http://127.0.0.1:8000/docs.