import requests
import json

# Local server URL (adjust if running on a different port)
URL = "http://127.0.0.1:8000/normalize"

test_cases = [
    "mujhe teen din se tez bukhaar hai",
    "sir mien drd horha hy",
    "mere pet mein bohat dard ho raha hai",
    "soraha hon", # Example provided by user
    "suraha hon", # Example provided by user
    "mjhe kansi he kafi",
    "pait mien shadeed drd hy"
]

def run_tests():
    print(f"{'INPUT':<40} | {'NORMALIZED':<40} | {'SYMPTOMS'}")
    print("-" * 100)
    
    for text in test_cases:
        try:
            response = requests.post(URL, json={"text": text})
            if response.status_code == 200:
                data = response.json()
                norm = data.get("normalized_text", "N/A")
                symptoms = ", ".join([s["symptom"] for s in data.get("symptoms", [])])
                print(f"{text:<40} | {norm:<40} | {symptoms}")
            else:
                print(f"Error for '{text}': {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to connect for '{text}': {e}")

if __name__ == "__main__":
    print("Testing MedBridge NLP Normalization...")
    print("Note: Make sure the FastAPI server is running (uvicorn main:app --reload)\n")
    run_tests()
