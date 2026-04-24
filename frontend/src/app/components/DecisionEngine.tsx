// import { AlertCircle, CheckCircle2 } from 'lucide-react';

// interface DecisionEngineProps {
//   userInput?: string;
// }

// export function DecisionEngine({ userInput = "stomach pain and fever" }: DecisionEngineProps) {
//   const verdict = 'stay'; // 'stay' or 'hospital'
//   const severity = 'moderate';

//   return (
//     <div className="flex flex-col h-full overflow-y-auto">
//       {/* Header */}
//       <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
//         <h2 className="text-white text-2xl">Go or Stay Home</h2>
//         <p className="text-white/90 text-sm mt-1">Analyzing: "{userInput}"</p>
//       </div>

//       {/* Main Content */}
//       <div className="px-6 py-6 space-y-5">
//         {/* High-Impact Verdict Card */}
//         <div
//           className="rounded-[32px] p-8 shadow-lg border-4"
//           style={{
//             backgroundColor: verdict === 'stay' ? '#26A68A' : '#d4183d',
//             borderColor: verdict === 'stay' ? '#1a7a5e' : '#b01530'
//           }}
//         >
//           <div className="flex items-center justify-center mb-4">
//             <div
//               className="w-24 h-24 rounded-full flex items-center justify-center shadow-xl"
//               style={{
//                 backgroundColor: verdict === 'stay' ? '#E2F9D3' : '#ffe0e0'
//               }}
//             >
//               <CheckCircle2
//                 className="w-16 h-16"
//                 style={{
//                   color: verdict === 'stay' ? '#26A68A' : '#d4183d'
//                 }}
//               />
//             </div>
//           </div>
//           <h2 className="text-4xl text-center mb-3 text-white uppercase tracking-wide">
//             {verdict === 'stay' ? 'STAY HOME' : 'GO TO HOSPITAL NOW'}
//           </h2>
//           <p className="text-center text-white text-xl">
//             {verdict === 'stay' ? 'Monitor symptoms & rest' : 'Immediate medical attention needed'}
//           </p>
//         </div>

//         {/* Severity Indicator */}
//         <div className="bg-white rounded-[32px] p-6">
//           <h3 className="mb-4" style={{ color: '#136382' }}>Severity Level</h3>
//           <div className="flex items-center gap-4">
//             <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
//               <div
//                 className="h-full rounded-full transition-all"
//                 style={{
//                   width: severity === 'low' ? '33%' : severity === 'moderate' ? '66%' : '100%',
//                   backgroundColor: severity === 'low' ? '#26A68A' : severity === 'moderate' ? '#FFA500' : '#d4183d'
//                 }}
//               />
//             </div>
//             <span className="text-base capitalize" style={{ color: '#136382' }}>{severity}</span>
//           </div>
//         </div>

//         {/* 3 Bulleted Reasons */}
//         <div className="bg-white rounded-[32px] p-6 shadow-sm">
//           <h3 className="mb-5 flex items-center gap-2 text-xl" style={{ color: '#136382' }}>
//             <AlertCircle className="w-6 h-6" />
//             Why This Decision?
//           </h3>
//           <div className="space-y-4">
//             <div className="flex gap-4">
//               <div
//                 className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white"
//                 style={{ backgroundColor: '#26A68A' }}
//               >
//                 1
//               </div>
//               <p className="text-gray-800 leading-relaxed text-base pt-1">
//                 Your symptoms indicate a common viral infection that typically resolves with rest
//               </p>
//             </div>
//             <div className="flex gap-4">
//               <div
//                 className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white"
//                 style={{ backgroundColor: '#26A68A' }}
//               >
//                 2
//               </div>
//               <p className="text-gray-800 leading-relaxed text-base pt-1">
//                 No red flags detected (fever below 102°F, no breathing difficulty)
//               </p>
//             </div>
//             <div className="flex gap-4">
//               <div
//                 className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white"
//                 style={{ backgroundColor: '#26A68A' }}
//               >
//                 3
//               </div>
//               <p className="text-gray-800 leading-relaxed text-base pt-1">
//                 Symptoms started recently (within 24 hours) with gradual onset
//               </p>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
import { useState } from "react";
import { AlertCircle, CheckCircle2, XCircle } from 'lucide-react';

interface DecisionEngineProps {
  userInput?: string;
}

interface GoOrStayResult {
  verdict: "GO" | "STAY";
  urgency: "Immediate" | "Within 24hrs" | "Can wait";
  reasons: string[];
  disclaimer: string;
}

export function DecisionEngine({ userInput = "stomach pain and fever" }: DecisionEngineProps) {
  const [result, setResult] = useState<GoOrStayResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("http://127.0.0.1:8000/go-or-stay", {
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

  const verdict = result?.verdict === "GO" ? "hospital" : "stay";
  const severity =
    result?.urgency === "Immediate" ? "high" :
    result?.urgency === "Within 24hrs" ? "moderate" : "low";

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
        <h2 className="text-white text-2xl">Go or Stay Home</h2>
        <p className="text-white/90 text-sm mt-1">Analyzing: "{userInput}"</p>
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

        {/* Result */}
        {result && (
          <>
            {/* Verdict Card */}
            <div
              className="rounded-[32px] p-8 shadow-lg border-4"
              style={{
                backgroundColor: verdict === 'stay' ? '#26A68A' : '#d4183d',
                borderColor: verdict === 'stay' ? '#1a7a5e' : '#b01530'
              }}
            >
              <div className="flex items-center justify-center mb-4">
                <div
                  className="w-24 h-24 rounded-full flex items-center justify-center shadow-xl"
                  style={{ backgroundColor: verdict === 'stay' ? '#E2F9D3' : '#ffe0e0' }}
                >
                  {verdict === 'stay'
                    ? <CheckCircle2 className="w-16 h-16" style={{ color: '#26A68A' }} />
                    : <XCircle className="w-16 h-16" style={{ color: '#d4183d' }} />
                  }
                </div>
              </div>
              <h2 className="text-4xl text-center mb-3 text-white uppercase tracking-wide">
                {verdict === 'stay' ? 'STAY HOME' : 'GO TO HOSPITAL NOW'}
              </h2>
              <p className="text-center text-white text-xl">
                {verdict === 'stay' ? 'Monitor symptoms & rest' : 'Immediate medical attention needed'}
              </p>
            </div>

            {/* Severity Indicator */}
            <div className="bg-white rounded-[32px] p-6">
              <h3 className="mb-4" style={{ color: '#136382' }}>Severity Level</h3>
              <div className="flex items-center gap-4">
                <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: severity === 'low' ? '33%' : severity === 'moderate' ? '66%' : '100%',
                      backgroundColor: severity === 'low' ? '#26A68A' : severity === 'moderate' ? '#FFA500' : '#d4183d'
                    }}
                  />
                </div>
                <span className="text-base capitalize" style={{ color: '#136382' }}>
                  {result.urgency}
                </span>
              </div>
            </div>

            {/* Reasons */}
            <div className="bg-white rounded-[32px] p-6 shadow-sm">
              <h3 className="mb-5 flex items-center gap-2 text-xl" style={{ color: '#136382' }}>
                <AlertCircle className="w-6 h-6" />
                Why This Decision?
              </h3>
              <div className="space-y-4">
                {result.reasons.map((reason, index) => (
                  <div key={index} className="flex gap-4">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white"
                      style={{ backgroundColor: verdict === 'stay' ? '#26A68A' : '#d4183d' }}
                    >
                      {index + 1}
                    </div>
                    <p className="text-gray-800 leading-relaxed text-base pt-1">{reason}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Disclaimer */}
            <p className="text-center text-xs text-gray-400 px-4 pb-2">{result.disclaimer}</p>

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