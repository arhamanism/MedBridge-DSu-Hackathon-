import { useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, MessageCircle } from 'lucide-react';

interface SymptomCheckerProps {
  userInput?: string;
}

interface Condition {
  name: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  description: string;
}

interface SymptomResponse {
  is_medical_input?: boolean;
  message?: string | null;
  conditions: Condition[];
  home_care_tips: string[];
  red_flags: string[];
  disclaimer: string;
}

const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;

export function SymptomChecker({ userInput = "" }: SymptomCheckerProps) {
  const [result, setResult] = useState<SymptomResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    if (!userInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/symptoms`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: userInput }),
      });
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Could not connect to MedBridge server. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
        <h2 className="text-white text-2xl">Symptom Analysis</h2>
        <p className="text-white/90 text-sm mt-1">Based on: "{userInput}"</p>
      </div>

      <div className="px-6 py-6 space-y-5">
        {/* Analyze Button */}
        {!result && !loading && (
          <button
            onClick={analyze}
            className="w-full py-4 rounded-[32px] text-white text-lg font-semibold shadow-md transition-opacity hover:opacity-90"
            style={{ backgroundColor: '#136382' }}
          >
            Analyze Symptoms
          </button>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin"
              style={{ borderColor: '#136382', borderTopColor: 'transparent' }} />
            <p className="text-gray-500">Analyzing your symptoms...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-[20px] p-4 text-red-600 text-sm text-center">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <>
            {/* Non-Medical Input Message */}
            {result.is_medical_input === false && (
              <div
                className="rounded-[32px] p-8 text-center"
                style={{ backgroundColor: '#D1EBEF' }}
              >
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                  style={{ backgroundColor: '#136382' }}
                >
                  <MessageCircle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl mb-3" style={{ color: '#136382' }}>
                  Hello!
                </h3>
                <p className="text-gray-600 mb-4 leading-relaxed">
                  {result.message || "Please tell me what symptoms you're experiencing so I can help you."}
                </p>
                <p className="text-sm text-gray-500">
                  {result.disclaimer || "Describe symptoms like: headache, fever, cough, pain, etc."}
                </p>
              </div>
            )}

            {/* Medical Results */}
            {(result.is_medical_input !== false && result.conditions.length > 0) && (
              <>
                {/* Condition Cards */}
                <div>
                  <h3 className="mb-4" style={{ color: '#136382' }}>Possible Conditions</h3>
                  <div className="space-y-4">
                    {result.conditions.map((condition, idx) => (
                      <div key={idx} className="bg-white rounded-[28px] p-5 border border-gray-100 shadow-sm">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h4 className="text-lg mb-1" style={{ color: '#136382' }}>
                              {condition.name}
                            </h4>
                            <p className="text-sm text-gray-600">{condition.description}</p>
                          </div>
                          {condition.severity === 'high' && (
                            <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 ml-2" />
                          )}
                        </div>

                        {/* Confidence Bar */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Confidence</span>
                            <span style={{ color: '#136382' }}>{condition.confidence}%</span>
                          </div>
                          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${condition.confidence}%`,
                                backgroundColor: condition.severity === 'high' ? '#d4183d' :
                                  condition.severity === 'medium' ? '#FFA500' : '#26A68A'
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Red Flag Warning */}
                {result.red_flags.length > 0 && (
                  <div className="bg-red-50 border-2 border-red-200 rounded-[28px] p-5">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
                      <div>
                        <h4 className="text-red-600 mb-2">Red Flags - Seek Immediate Care If:</h4>
                        <ul className="space-y-1 text-sm text-red-700">
                          {result.red_flags.map((flag, idx) => (
                            <li key={idx}>• {flag}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Home Care Checklist */}
                {result.home_care_tips.length > 0 && (
                  <div className="bg-white rounded-[28px] p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <CheckCircle2 className="w-6 h-6" style={{ color: '#26A68A' }} />
                      <h3 style={{ color: '#136382' }}>Home Care Checklist</h3>
                    </div>
                    <div className="space-y-3">
                      {result.home_care_tips.map((tip, idx) => (
                        <label key={idx} className="flex items-start gap-3 cursor-pointer group">
                          <input
                            type="checkbox"
                            className="w-5 h-5 mt-0.5 rounded accent-[#26A68A] cursor-pointer"
                          />
                          <span className="text-gray-700 leading-relaxed group-hover:text-gray-900">
                            {tip}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* Disclaimer */}
                <p className="text-center text-xs text-gray-400 px-4 pb-2">{result.disclaimer}</p>
              </>
            )}

            {/* Analyze Again */}
            <button
              onClick={() => { setResult(null); setError(null); }}
              className="w-full py-3 rounded-[32px] border-2 text-sm font-medium transition-opacity hover:opacity-80"
              style={{ borderColor: '#136382', color: '#136382' }}
            >
              Analyze Again
            </button>
          </>
        )}
      </div>
    </div>
  );
}
