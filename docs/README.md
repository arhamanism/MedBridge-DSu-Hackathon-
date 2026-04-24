# HealthAI Pakistan - Smart Health Assistant

## Overview
HealthAI Pakistan is an AI-powered health assistant that helps users make informed medical decisions. It provides symptom analysis, medication safety checks, doctor recommendations, and hospital decision support.

## Features

### 🎤 Voice Input & Symptom Extraction
- Converts Hindi/Urdu speech to Roman Urdu text
- Removes greetings and irrelevant content
- Extracts only symptom-related information
- Warns if no symptoms detected

### 🏥 Symptom Analysis
- AI-powered symptom checker
- Identifies possible conditions with confidence levels
- Provides red flag warnings for serious symptoms
- Offers home care recommendations

### 💊 Medicine Safety
- Drug interaction checker
- Generic alternative finder (verified Pakistani brands only)
- Prescription OCR for medicine extraction
- Strong disclaimers for medical safety

### 👨‍⚕️ Doctor Finder
- Recommends appropriate specialists
- Shows consultation fees in PKR
- Cost-saving recommendations
- Child-specific specialists

### 🏨 Hospital Decision
- "Go or Stay Home" recommendations
- Urgency level assessment
- Emergency warnings for critical symptoms

## Tech Stack

### Backend (FastAPI)
- **Language**: Python
- **AI Models**: Groq API (LLM), Whisper (Speech-to-text)
- **Database**: None (stateless API)
- **Deployment**: Render.com

### Frontend (React + Vite)
- **Framework**: React with TypeScript
- **UI Components**: shadcn/ui + Material-UI
- **Styling**: Tailwind CSS
- **Deployment**: Vercel

## Project Structure

```
HealthAI-Pakistan/
├── backend/
│   ├── main.py                    # Main FastAPI app
│   └── modules/
│       ├── symptom_analyzer.py    # Symptom checking
│       ├── medicine_safety.py     # Drug interactions
│       ├── doctor_finder.py       # Specialist recommendations
│       └── hospital_decision.py   # Go/stay decisions
├── frontend/
│   ├── src/app/
│   │   └── components/
│   │       ├── InputHub.tsx       # Voice input
│   │       ├── SymptomChecker.tsx # Symptom UI
│   │       ├── MedicationChecker.tsx # Medicine UI
│   │       ├── SpecialistRecommender.tsx # Doctor UI
│   │       └── DecisionEngine.tsx # Hospital UI
│   └── package.json
└── docs/
    ├── README.md                  # This file
    ├── DEPLOYMENT.md              # Deployment guide
    └── TEST_PLAN.md               # Test cases
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
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

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcribe` | Audio to text with symptom extraction |
| POST | `/symptoms` | Symptom analysis |
| POST | `/medications` | Drug interaction check |
| POST | `/alternatives` | Generic medicine finder |
| POST | `/specialist` | Doctor recommendations |
| POST | `/go-or-stay` | Hospital decision |
| POST | `/extract-medicines` | Prescription OCR |

## Important Notes

### Medical Disclaimer
⚠️ **This is not a substitute for professional medical advice.** Always consult a qualified healthcare provider for medical concerns.

### Medicine Information
- All brand names and prices are AI-generated for demonstration
- Always verify with a licensed pharmacist before purchasing
- Only buy from registered pharmacies

### Rate Limits
- Groq API: 20 requests/minute (free tier)
- Consider upgrading for production use

## Deployment

### Backend (Render.com)
1. Push to GitHub
2. Create new Web Service on Render
3. Connect repository, select `backend/` folder
4. Set environment variables
5. Deploy

### Frontend (Vercel)
1. Connect GitHub repository
2. Select `frontend/` folder
3. Set `VITE_BACKEND_URL` environment variable
4. Deploy

## Testing

Run comprehensive tests:
```bash
python docs/comprehensive_test.py
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create GitHub issue
- Check documentation in `/docs`
- Review test cases in `docs/TEST_PLAN.md`

---

**Made for Pakistan healthcare 🇵🇰**
