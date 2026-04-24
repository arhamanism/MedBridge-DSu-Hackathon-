# HealthAI Pakistan 🇵🇰

**AI-Powered Health Assistant for Pakistani Healthcare**

A comprehensive health assistant that helps users make informed medical decisions through voice input, symptom analysis, medication safety checks, and doctor recommendations.

## ✨ Features

### 🎤 **Voice Input & Symptom Extraction**
- **Multilingual Support**: Converts Hindi/Urdu speech to Roman Urdu text
- **Smart Filtering**: Removes greetings and irrelevant content
- **Symptom-Only Extraction**: Keeps only medical symptoms
- **Warning System**: Alerts when no symptoms are detected

### 🏥 **Symptom Analysis**
- **AI-Powered Diagnosis**: Identifies possible conditions with confidence levels
- **Red Flag Detection**: Warns about serious symptoms requiring immediate attention
- **Home Care Recommendations**: Provides self-care advice for mild cases
- **Emergency Alerts**: Critical symptom warnings

### 💊 **Medicine Safety**
- **Drug Interaction Checker**: Identifies dangerous medication combinations
- **Generic Alternative Finder**: Suggests verified Pakistani generic brands
- **Prescription OCR**: Extracts medicine names from prescription images
- **Safety Disclaimers**: Strong warnings about AI-generated information

### 👨‍⚕️ **Doctor Finder**
- **Smart Specialist Matching**: Recommends appropriate doctors based on symptoms
- **Cost Information**: Shows consultation fees in PKR
- **Money-Saving Tips**: Suggests cost-effective healthcare paths
- **Child Specialists**: Pediatric recommendations for children's symptoms

### 🏨 **Hospital Decision**
- **Go or Stay Home**: Clear recommendations on whether to visit hospital
- **Urgency Assessment**: Levels from "Can wait" to "Immediate"
- **Emergency Warnings**: Critical symptoms requiring immediate care
- **Time-Sensitive Advice**: When to seek urgent care vs emergency

## 🛠 Tech Stack

### Backend (FastAPI)
- **Framework**: FastAPI with Python
- **AI Models**: 
  - Groq API (LLaMA 3.3 70B) for medical analysis
  - Whisper (Speech-to-text) for voice input
  - LLaMA 4 Scout for prescription OCR
- **Architecture**: RESTful API, stateless
- **Deployment**: Render.com

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Components**: shadcn/ui + Material-UI
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Deployment**: Vercel

## 📁 Project Structure

```
HealthAI-Pakistan/
├── backend/
│   ├── main.py                    # Main FastAPI application
│   ├── requirements.txt           # Python dependencies
│   └── modules/
│       ├── symptom_analyzer.py    # Symptom analysis logic
│       ├── medicine_safety.py     # Drug interactions & alternatives
│       ├── doctor_finder.py       # Specialist recommendations
│       └── hospital_decision.py   # Go/stay decision logic
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── components/
│   │       │   ├── InputHub.tsx       # Voice input interface
│   │       │   ├── SymptomChecker.tsx # Symptom analysis UI
│   │       │   ├── MedicationChecker.tsx # Medicine safety UI
│   │       │   ├── SpecialistRecommender.tsx # Doctor finder UI
│   │       │   └── DecisionEngine.tsx # Hospital decision UI
│   │       └── App.tsx              # Main React app
│   ├── package.json               # Frontend dependencies
│   └── vite.config.ts            # Vite configuration
└── docs/
    ├── README.md                  # This file
    ├── DEPLOYMENT.md              # Deployment guide
    └── TEST_PLAN.md               # Test cases and demo script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API key (free at console.groq.com)

### Backend Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd HealthAI-Pakistan

# Set up Python environment
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env

# Start backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `.env` in backend folder:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcribe` | Audio to text with symptom extraction |
| POST | `/symptoms` | Symptom analysis and condition identification |
| POST | `/medications` | Drug interaction safety check |
| POST | `/alternatives` | Generic medicine alternatives |
| POST | `/specialist` | Doctor/specialist recommendations |
| POST | `/go-or-stay` | Hospital vs home care decision |
| POST | `/extract-medicines` | Prescription OCR extraction |

### Example API Usage
```python
# Symptom analysis
response = requests.post("http://localhost:8000/symptoms", 
    json={"text": "I have headache and fever"})

# Medication safety check
response = requests.post("http://localhost:8000/medications",
    json={"medicines": ["Panadol", "Aspirin"]})
```

## 🧪 Testing

Run comprehensive tests:
```bash
python docs/comprehensive_test.py
```

Key test cases:
- ✅ Voice transcription with symptom extraction
- ✅ Dangerous drug interaction detection
- ✅ Generic medicine suggestions
- ✅ Emergency symptom identification
- ✅ Specialist matching accuracy

## 🌐 Deployment

### Single Repository Approach ✅
**Yes, you can work with one repository!** The backend and frontend are in the same repo:

1. **Backend** deploys to Render.com from `backend/` folder
2. **Frontend** deploys to Vercel from `frontend/` folder
3. **Both** use the same GitHub repository

### Backend Deployment (Render.com)
1. Push to GitHub
2. Go to Render.com → New Web Service
3. Connect your GitHub repository
4. **Root Directory**: `backend`
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. **Environment Variables**: Add `GROQ_API_KEY`

### Frontend Deployment (Vercel)
1. Go to Vercel.com → New Project
2. Connect your GitHub repository
3. **Root Directory**: `frontend`
4. **Build Command**: `npm install && npm run build`
5. **Output Directory**: `dist`
6. **Environment Variables**: `VITE_BACKEND_URL=https://your-backend.onrender.com`

## ⚠️ Important Disclaimers

### Medical Safety
- **Not a substitute for professional medical advice**
- Always consult qualified healthcare providers
- Emergency symptoms require immediate hospital visit

### Medicine Information
- **AI-generated for demonstration purposes**
- All brand names and prices are estimates
- **Always verify with licensed pharmacist**
- Only purchase from registered pharmacies

### Rate Limits
- Groq API: 20 requests/minute (free tier)
- Consider upgrading for production use

## 🎯 Demo Script (3 Minutes)

1. **Voice Input** (30s)
   - Record: "Mujhe sar dard hai aur bukhar hai"
   - Show: Clean symptom extraction

2. **Symptom Analysis** (45s)
   - Display: Possible conditions with confidence
   - Highlight: Red flag warnings

3. **Medication Safety** (60s)
   - Add: Brufen, Panadol
   - Show: Safe interactions + generic alternatives
   - Emphasize: Safety disclaimers

4. **Emergency Case** (30s)
   - Input: "Chest pain, difficulty breathing"
   - Show: "GO TO HOSPITAL NOW" alert

5. **Close** (15s)
   - "Helps patients make informed decisions"

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit: `git commit -m "Add feature description"`
5. Push: `git push origin feature-name`
6. Create Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check `/docs` folder
- **Testing**: Follow `docs/TEST_PLAN.md`

---

**Made with ❤️ for Pakistan Healthcare 🇵🇰**

*Empowering patients to make informed healthcare decisions with AI*
