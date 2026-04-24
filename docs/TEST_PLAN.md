# MedBridge Test Plan - Hackathon Demo

## Quick Test Checklist

---

## 1. VOICE INPUT & SYMPTOM EXTRACTION

### Test Case 1.1: Clean Symptom Input
**Say**: "Mujhe sar dard hai aur bukhar hai kal se"

**Expected**:
- ✅ Transcript shows: "sar dard hai aur bukhar hai kal se"
- ✅ No warning shown
- ✅ Can proceed to modules

### Test Case 1.2: Greeting + Symptoms
**Say**: "Assalamualaikum doctor sahab, mujhe pet mein dard hai"

**Expected**:
- ✅ Transcript shows: "pet mein dard hai" (greeting removed)
- ✅ No warning

### Test Case 1.3: Only Greeting (No Symptoms)
**Say**: "Hello, my name is Ali, how are you today"

**Expected**:
- ⚠️ Orange warning banner appears
- ⚠️ Message: "Please describe your symptoms..."
- ✅ Shows `has_symptoms: false`

### Test Case 1.4: Mixed Hindi/Urdu
**Say**: "मुझे सीने में दर्द है और सांस फूल रही है"

**Expected**:
- ✅ Normalizes to: "seene mein dard hai aur saans phool rahi hai"

---

## 2. SYMPTOM CHECKER MODULE

### Test Case 2.1: Common Symptoms
**Input**: "I have headache, fever, and sore throat"

**Expected**:
- ✅ Returns possible conditions
- ✅ Shows confidence levels
- ✅ Gives recommendations

### Test Case 2.2: Serious Symptoms
**Input**: "Chest pain, difficulty breathing, sweating"

**Expected**:
- ⚠️ Shows "Seek immediate medical attention" warning
- ✅ High urgency recommendation

### Test Case 2.3: Non-Medical Input
**Input**: "What's the weather today"

**Expected**:
- ⚠️ Friendly message: "I don't see any medical symptoms..."
- ✅ No hallucinated conditions

---

## 3. MEDICATION CHECKER

### Test Case 3.1: Safe Single Medicine
**Input**: Panadol

**Expected**:
- ✅ Shows "Safe to use"
- ✅ No interactions

### Test Case 3.2: Multiple Safe Medicines
**Input**: Panadol, Calpol, Vitamin C

**Expected**:
- ✅ Shows low/no risk interactions
- ✅ Alternatives show (if brand names given)

### Test Case 3.3: Dangerous Combination
**Input**: Diclofenac, Aspirin, Ibuprofen (3 NSAIDs)

**Expected**:
- ⚠️ **HIGH RISK** warning for multiple NSAIDs
- ✅ Specific warning about GI bleeding
- ✅ Red/orange alert styling

### Test Case 3.4: Real Generic Alternatives
**Input**: Brufen, Panadol

**Expected**:
- ✅ Shows real brands: Voveran, Calpol
- ✅ Prices in PKR
- ✅ Savings percentage realistic (20-50%)
- ⚠️ Orange disclaimer visible

### Test Case 3.5: Already Generic
**Input**: Paracetamol, Ibuprofen

**Expected**:
- ✅ Message: "Already using generics"
- ✅ Empty alternatives list

---

## 4. SPECIALIST RECOMMENDER

### Test Case 4.1: General Symptoms
**Input**: "Headache, fever, body pain"

**Expected**:
- ✅ Suggests: General Physician (not specialist)
- ✅ Match percentage 80-95%

### Test Case 4.2: Specific Symptoms
**Input**: "Chest pain, palpitations"

**Expected**:
- ✅ Suggests: Cardiologist
- ✅ High match percentage

### Test Case 4.3: Child Symptoms
**Input**: "Child has fever and cough"

**Expected**:
- ✅ Suggests: Pediatrician

---

## 5. GO OR STAY DECISION

### Test Case 5.1: Stay Home
**Input**: "Mild headache, feeling tired"

**Expected**:
- 🟢 Decision: "Stay Home"
- ✅ Self-care recommendations
- ✅ When to seek help guidelines

### Test Case 5.2: Go to Hospital
**Input**: "Severe chest pain, can't breathe"

**Expected**:
- 🔴 Decision: "Go to Hospital NOW"
- ⚠️ Emergency warning
- ✅ Nearest hospital info

### Test Case 5.3: Monitor/Urgent Care
**Input**: "Fever for 3 days, not reducing with medicine"

**Expected**:
- 🟡 Decision: "Visit Doctor Today"
- ✅ Time-sensitive warning

---

## 6. PRESCRIPTION OCR (Image Upload)

### Test Case 6.1: Clear Prescription
**Upload**: Clear prescription image with medicine names

**Expected**:
- ✅ Extracts medicine names correctly
- ✅ Shows extracted list
- ✅ Can run interaction check on extracted meds

### Test Case 6.2: Blurry/Unclear Image
**Upload**: Blurry image

**Expected**:
- ⚠️ Error: "Could not extract medicines"
- ✅ Suggestion to enter manually

---

## 7. MOBILE RESPONSIVENESS

### Test on Phone:
- ✅ Voice recording button works
- ✅ Text is readable
- ✅ Cards scroll properly
- ✅ No horizontal scrolling issues
- ✅ Touch targets are big enough

---

## DEMO FLOW (For Judges)

### 3-Minute Demo Script:

1. **Voice Input** (30 sec)
   - Record: "Mujhe sar dard hai aur bukhar hai"
   - Show: Clean extraction, no warning

2. **Symptom Checker** (45 sec)
   - Click "Symptom Checker"
   - Show: AI analysis, conditions, recommendations

3. **Medication Safety** (60 sec)
   - Go to "Medication Checker"
   - Add: Brufen, Panadol
   - Show: Interactions (safe)
   - Show: Generic alternatives (Voveran, Calpol)
   - Point out: Orange disclaimer warning

4. **Serious Case** (30 sec)
   - New input: "Chest pain, difficulty breathing"
   - Go/Stay: Shows RED "Go to Hospital"

5. **Closing** (15 sec)
   - "This helps patients make informed decisions before seeing a doctor"

---

## BUG REPORTING

If something breaks, note:
1. What you did
2. What you expected
3. What actually happened
4. Screenshot if possible

---

## BACKEND HEALTH CHECKS

```bash
# Test if backend is running
curl http://localhost:8000/

# Should return:
# {"status": "MedBridge Voice API running"}

# Test symptom endpoint
curl -X POST http://localhost:8000/symptoms \
  -H "Content-Type: application/json" \
  -d '{"text": "headache and fever"}'
```

---

## EMERGENCY FALLBACKS

If demo fails:
1. **Backend down**: Show screenshots from testing
2. **Groq API limit**: Show cached responses
3. **Voice not working**: Type input manually
4. **Mobile issues**: Demo on laptop only

---

## CHECKLIST BEFORE PRESENTING

- [ ] Backend running on localhost:8000
- [ ] Frontend running on localhost:5173
- [ ] Voice test completed successfully
- [ ] Medication checker shows real brands
- [ ] Mobile test done (if showing on phone)
- [ ] GROQ_API_KEY has credits left
- [ ] Screenshot backup ready
- [ ] 3G/4G hotspot as backup WiFi

---

## KNOWN LIMITATIONS (Be Honest with Judges)

1. **Medicine names**: AI-generated for demo, not real-time pharmacy data
2. **Prices**: Estimated, not live market prices
3. **Not a substitute**: Always see a real doctor for diagnosis
4. **Groq API**: Rate limited (20 requests/min on free tier)

---

**Good luck with the demo! 🚀**
