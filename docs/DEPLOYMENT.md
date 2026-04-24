# MedBridge Deployment Guide

## Project Structure

```
MedBridge-DSu-Hackathon--main/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main FastAPI app with all endpoints
│   ├── modules/               # Backend logic modules
│   │   ├── symptom_checker.py
│   │   ├── medication_checker.py
│   │   ├── specialist_recommender.py
│   │   └── go_or_stay.py
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Vite Frontend
│   ├── src/
│   │   └── app/
│   │       ├── components/
│   │       │   ├── InputHub.tsx
│   │       │   ├── SymptomChecker.tsx
│   │       │   ├── MedicationChecker.tsx
│   │       │   ├── SpecialistRecommender.tsx
│   │       │   └── DecisionEngine.tsx
│   │       └── App.tsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── .env                        # Environment variables (create this)
└── DEPLOYMENT.md              # This file
```

## What to Deploy

### Backend (FastAPI)
**File**: `backend/main.py`  
**Port**: 8000  
**Requirements**: `backend/requirements.txt`

**Endpoints**:
- `POST /transcribe` - Audio to text (Whisper AI)
- `POST /symptoms` - Symptom analysis
- `POST /medications` - Drug interaction check
- `POST /specialist` - Doctor recommendations
- `POST /go-or-stay` - Hospital vs home care
- `POST /extract-medicines` - Prescription OCR
- `POST /alternatives` - Generic medicine finder

### Frontend (React + Vite)
**Build command**: `npm run build`  
**Output**: `frontend/dist/`  
**Static hosting**: Serve `dist/` folder

## Environment Variables

Create `.env` in backend folder:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get key from: https://console.groq.com/keys

## Local Development

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment Options

### Option 1: Free - Render.com (Recommended)

**Backend**:
1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect repo, select `backend/` folder
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add env var: `GROQ_API_KEY`

**Frontend**:
1. New Static Site on Render
2. Build Command: `cd frontend && npm install && npm run build`
3. Publish Directory: `frontend/dist`
4. Add rewrite rule: `/*` → `/index.html`

### Option 2: Free - Vercel (Frontend) + Railway (Backend)

**Backend on Railway**:
```bash
# Install Railway CLI
npm i -g @railway/cli
railway login
railway init
cd backend
railway up
```

**Frontend on Vercel**:
```bash
npm i -g vercel
cd frontend
vercel --prod
```

### Option 3: VPS (DigitalOcean/AWS)

```bash
# Server setup
sudo apt update
sudo apt install python3-pip nodejs npm

# Clone repo
git clone <your-repo>
cd MedBridge-DSu-Hackathon--main

# Backend
cd backend
pip3 install -r requirements.txt
# Create systemd service or use PM2

# Frontend
cd ../frontend
npm install
npm run build
# Serve dist/ with nginx
```

## Important Deployment Notes

1. **CORS**: Already configured to allow `*` origins
2. **Groq API**: Has rate limits (free tier: 20 req/min)
3. **Whisper Model**: Downloads ~500MB on first run
4. **Environment**: Must set `GROQ_API_KEY` in production

## Frontend Environment

Create `frontend/.env.production`:
```env
VITE_BACKEND_URL=https://your-backend-url.onrender.com
```

## Checklist Before Demo

- [ ] Backend deployed and health check passes
- [ ] Frontend deployed and connects to backend
- [ ] GROQ_API_KEY set in production
- [ ] Test voice transcription works
- [ ] Test symptom checker works
- [ ] Test medication checker works
- [ ] Test on mobile (responsive)

## Quick Test Commands

```bash
# Test backend health
curl https://your-backend.com/

# Test transcribe endpoint
curl -X POST -F "audio=@test.wav" https://your-backend.com/transcribe

# Test symptoms
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "I have headache and fever"}' \
  https://your-backend.com/symptoms
```

## Support

- Groq Docs: https://console.groq.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Vite Docs: https://vitejs.dev/guide/static-deploy.html
