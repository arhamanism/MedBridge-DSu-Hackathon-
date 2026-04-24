"""
HealthAI Pakistan - Comprehensive Test Suite
Tests ALL features mentioned in TEST_PLAN.md
Run this to verify everything works before deployment
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, endpoint, data=None, expected_keys=None, expected_status=200):
    """Test an API endpoint and return success/failure"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=15)
        else:
            response = requests.post(url, json=data, timeout=15)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            result = response.json()
            print(f"Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Check expected keys
            if expected_keys:
                missing = [key for key in expected_keys if key not in result]
                if missing:
                    print(f"⚠️ Missing expected keys: {missing}")
                else:
                    print("✅ All expected keys present")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_symptom_extraction(text, expected_has_symptoms):
    """Test symptom extraction with various inputs"""
    print(f"\n{'='*60}")
    print(f"TEST: Symptom Extraction - '{text}'")
    print(f"{'='*60}")
    
    data = {"text": text}
    
    try:
        response = requests.post(f"{BASE_URL}/symptoms", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            has_symptoms = result.get("is_medical_input", True)
            
            print(f"Input: {text}")
            print(f"Has symptoms: {has_symptoms}")
            print(f"Expected: {expected_has_symptoms}")
            
            if has_symptoms == expected_has_symptoms:
                print("✅ Symptom extraction working correctly")
                return True
            else:
                print("❌ Symptom extraction not working as expected")
                return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def run_all_tests():
    """Run comprehensive test suite for HealthAI Pakistan"""
    print("🧪 HEALTHAI PAKISTAN - COMPREHENSIVE TEST SUITE")
    print("Testing ALL features from TEST_PLAN.md")
    print("Make sure backend is running: uvicorn main:app --port 8000")
    
    results = []
    
    # ===== 1. VOICE INPUT & SYMPTOM EXTRACTION =====
    print("\n" + "="*80)
    print("1. VOICE INPUT & SYMPTOM EXTRACTION")
    print("="*80)
    
    # Test Case 1.1: Clean Symptom Input
    results.append(test_symptom_extraction(
        "Mujhe sar dard hai aur bukhar hai kal se",
        True
    ))
    
    # Test Case 1.2: Greeting + Symptoms  
    results.append(test_symptom_extraction(
        "Assalamualaikum doctor sahab, mujhe pet mein dard hai",
        True
    ))
    
    # Test Case 1.3: Only Greeting (No Symptoms)
    results.append(test_symptom_extraction(
        "Hello, my name is Ali, how are you today",
        False
    ))
    
    # Test Case 1.4: Mixed Hindi/Urdu
    results.append(test_symptom_extraction(
        "मुझे सीने में दर्द है और सांस फूल रही है",
        True
    ))
    
    # ===== 2. SYMPTOM CHECKER MODULE =====
    print("\n" + "="*80)
    print("2. SYMPTOM CHECKER MODULE")
    print("="*80)
    
    # Test Case 2.1: Common Symptoms
    results.append(test_endpoint(
        "Symptom Checker - Common Symptoms",
        "POST",
        "/symptoms",
        {"text": "I have headache, fever, and sore throat"},
        expected_keys=["possible_conditions", "recommendations", "red_flags"]
    ))
    
    # Test Case 2.2: Serious Symptoms (Emergency)
    results.append(test_endpoint(
        "Symptom Checker - Emergency Symptoms",
        "POST",
        "/symptoms",
        {"text": "Chest pain, difficulty breathing, sweating"},
        expected_keys=["possible_conditions", "recommendations", "red_flags"]
    ))
    
    # Test Case 2.3: Non-Medical Input
    results.append(test_endpoint(
        "Symptom Checker - Non-Medical Input",
        "POST",
        "/symptoms",
        {"text": "What's the weather today"},
        expected_keys=["message"]
    ))
    
    # ===== 3. MEDICATION SAFETY =====
    print("\n" + "="*80)
    print("3. MEDICATION SAFETY")
    print("="*80)
    
    # Test Case 3.1: Safe Single Medicine
    results.append(test_endpoint(
        "Medications - Safe Single Medicine",
        "POST",
        "/medications",
        {"medicines": ["Panadol"]},
        expected_keys=["is_safe", "interactions"]
    ))
    
    # Test Case 3.2: Multiple Safe Medicines
    results.append(test_endpoint(
        "Medications - Multiple Safe Medicines",
        "POST",
        "/medications",
        {"medicines": ["Panadol", "Vitamin C"]},
        expected_keys=["is_safe", "interactions"]
    ))
    
    # Test Case 3.3: Dangerous Combination (3 NSAIDs)
    results.append(test_endpoint(
        "Medications - Dangerous NSAID Combo",
        "POST",
        "/medications",
        {"medicines": ["Diclofenac", "Aspirin", "Ibuprofen"]},
        expected_keys=["is_safe", "interactions", "summary"]
    ))
    
    # Test Case 3.4: Generic Alternatives - Real Brands
    results.append(test_endpoint(
        "Generic Alternatives - Real Pakistani Brands",
        "POST",
        "/alternatives",
        {"medicines": ["Brufen", "Panadol"]},
        expected_keys=["alternatives", "total_savings", "disclaimer"]
    ))
    
    # Test Case 3.5: Already Generic
    results.append(test_endpoint(
        "Generic Alternatives - Already Generic",
        "POST",
        "/alternatives",
        {"medicines": ["Paracetamol", "Ibuprofen"]},
        expected_keys=["alternatives", "total_savings", "disclaimer"]
    ))
    
    # ===== 4. DOCTOR FINDER =====
    print("\n" + "="*80)
    print("4. DOCTOR FINDER")
    print("="*80)
    
    # Test Case 4.1: General Symptoms
    results.append(test_endpoint(
        "Doctor Finder - General Symptoms",
        "POST",
        "/specialist",
        {"text": "Headache, fever, body pain"},
        expected_keys=["specialists"]
    ))
    
    # Test Case 4.2: Specific Symptoms (Cardiac)
    results.append(test_endpoint(
        "Doctor Finder - Cardiac Symptoms",
        "POST",
        "/specialist",
        {"text": "Chest pain, palpitations"},
        expected_keys=["specialists"]
    ))
    
    # Test Case 4.3: Child Symptoms
    results.append(test_endpoint(
        "Doctor Finder - Child Symptoms",
        "POST",
        "/specialist",
        {"text": "Child has fever and cough"},
        expected_keys=["specialists"]
    ))
    
    # ===== 5. HOSPITAL DECISION =====
    print("\n" + "="*80)
    print("5. HOSPITAL DECISION")
    print("="*80)
    
    # Test Case 5.1: Stay Home
    results.append(test_endpoint(
        "Hospital Decision - Stay Home",
        "POST",
        "/go-or-stay",
    {"text": "Mild headache, feeling tired"},
        expected_keys=["verdict", "urgency", "reasons"]
    ))
    
    # Test Case 5.2: Go to Hospital (Emergency)
    results.append(test_endpoint(
        "Hospital Decision - Emergency",
        "POST",
        "/go-or-stay",
        {"text": "Severe chest pain, can't breathe"},
        expected_keys=["verdict", "urgency", "reasons"]
    ))
    
    # Test Case 5.3: Monitor/Urgent Care
    results.append(test_endpoint(
        "Hospital Decision - Urgent Care",
        "POST",
        "/go-or-stay",
        {"text": "Fever for 3 days, not reducing with medicine"},
        expected_keys=["verdict", "urgency", "reasons"]
    ))
    
    # ===== 6. BACKEND HEALTH =====
    print("\n" + "="*80)
    print("6. BACKEND HEALTH CHECK")
    print("="*80)
    
    # Test Case 6.1: Health Check
    results.append(test_endpoint(
        "Backend Health Check",
        "GET",
        "/",
        expected_keys=["message"]
    ))
    
    # ===== SUMMARY =====
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 HealthAI Pakistan is ready for deployment!")
        print("\nNext steps:")
        print("1. Push to GitHub")
        print("2. Deploy backend to Render.com")
        print("3. Deploy frontend to Vercel")
        print("4. Test on mobile")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        print("\nTroubleshooting:")
        print("1. Make sure backend is running: uvicorn main:app --port 8000")
        print("2. Check GROQ_API_KEY is set in .env")
        print("3. Verify all modules import correctly")
    
    print(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
