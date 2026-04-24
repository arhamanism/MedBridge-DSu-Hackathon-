# MedBridge AI Backend 🏥

A robust, AI-powered backend designed for the Pakistani healthcare ecosystem. This project provides specialized endpoints for voice transcription and prescription analysis, leveraging state-of-the-art multimodal LLMs.

## 🚀 Key Features

### 1. Bilingual Voice Transcription (`/transcribe`)
- **Whisper Integration:** Uses `faster-whisper` (running on CUDA) for high-accuracy speech-to-text.
- **Roman Urdu Normalization:** Automatically detects and converts mixed English/Urdu speech into standardized Roman Urdu (WhatsApp style).
- **Medical Context Aware:** Optimized for doctor-patient interactions in the Pakistani context.

### 2. Prescription OCR & Generic Medicine Finder (`/prescription`)
- **Multimodal Analysis:** Uses **Meta Llama 4 Scout** on Groq for high-fidelity OCR of medical prescriptions, even with challenging handwriting.
- **Generic Substitution:** Automatically identifies the active chemical salts and suggests cheaper local generic alternatives available in Pakistan.
- **Safety First:** Built-in anti-hallucination logic that refuses to guess drug formulas for unknown regional brands, advising professional consultation instead.

## 🛠 Tech Stack
- **FastAPI:** High-performance web framework for Python.
- **Groq Cloud API:**
  - `meta-llama/llama-4-scout-17b-16e-instruct` (Vision OCR)
  - `llama-3.3-70b-versatile` (Normalization & Pharmacist Logic)
- **Faster-Whisper:** Efficient transformer-based speech recognition.
- **Python-Dotenv:** Secure environment variable management.

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arhamanism/MedBridge-DSu-Hackathon-.git
   cd MedBridge-DSu-Hackathon-
   ```

2. **Set up Virtual Environment:**
   ```bash
   python -m venv henv
   .\henv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Server:**
   ```bash
   cd backend
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

## 🧪 Testing
- Use `test_client.html` to test voice transcription via your microphone.
- Use `test_prescription_client.html` to test prescription OCR by uploading images.

---
*Built for the DSu Hackathon - Bridging the gap in Pakistani healthcare with AI.*
