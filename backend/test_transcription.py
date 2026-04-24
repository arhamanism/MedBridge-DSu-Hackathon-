from faster_whisper import WhisperModel
import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # never hardcode, use env variable

def load_model():
    print("Initializing Whisper model...")
    return WhisperModel("small", device="cuda", compute_type="float16")

def transcribe_audio(model, audio_path: str) -> tuple[str, str, float]:
    segments, info = model.transcribe(audio_path, beam_size=5)  # no language hardcoded
    
    full_text = ""
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        full_text += segment.text + " "
    
    return full_text.strip(), info.language, round(info.language_probability, 2)

def normalize_to_roman(text: str, detected_lang: str) -> str:
    # if already english, skip groq call entirely
    if detected_lang == "en":
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
                    "content": """You are a language normalizer for a Pakistani medical app.
Rules:
- Urdu script (ہ ی ا etc) → convert to Roman Urdu WhatsApp style
- Hindi/Devanagari script (क ख ग etc) → convert to Roman Urdu WhatsApp style  
- Roman Urdu already → clean up minor errors, return as is
- English → return exactly as is, no changes
- Mixed Urdu+English → keep English parts, convert only Urdu parts

Examples:
مجھے بخار ہے → mujhe bukhar hai
मुझे बुखार है → mujhe bukhar hai
I have fever → I have fever
sir mein dard hai → sir mein dard hai
mere pet mein bohat dard hai → mere pet mein bohat dard hai

Return only the final text. No explanation, no extra words."""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"].strip()

# test run
if __name__ == "__main__":
    path = "test_audio/testing_audio.mp3"
    
    if not os.path.exists(path):
        print(f"{path} not found")
        exit()
    
    model = load_model()
    raw, lang, confidence = transcribe_audio(model, path)
    
    print(f"\nDetected: {lang} ({confidence})")
    print(f"Raw: {raw}")
    
    normalized = normalize_to_roman(raw, lang)
    print(f"Normalized: {normalized}")