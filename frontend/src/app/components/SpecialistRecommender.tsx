// import { Stethoscope, Phone, Star } from 'lucide-react';

// interface SpecialistRecommenderProps {
//   userInput?: string;
// }

// export function SpecialistRecommender({ userInput = "digestive issues" }: SpecialistRecommenderProps) {
//   const specialists = [
//     {
//       type: 'Gastroenterologist',
//       reason: 'Best match for your digestive symptoms',
//       confidence: 95,
//       description: 'Specializes in stomach, intestine, and digestive system issues',
//       avgFee: '2,500 - 4,000 PKR'
//     },
//     {
//       type: 'General Physician',
//       reason: 'Can provide initial assessment',
//       confidence: 75,
//       description: 'General medical consultation and preliminary diagnosis',
//       avgFee: '1,000 - 2,000 PKR'
//     }
//   ];

//   return (
//     <div className="flex flex-col h-full overflow-y-auto">
//       {/* Header */}
//       <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
//         <h2 className="text-white text-2xl">Specialist Finder</h2>
//         <p className="text-white/90 text-sm mt-1">Based on: "{userInput}"</p>
//       </div>

//       {/* Main Content */}
//       <div className="px-6 py-6 space-y-5">
//         {/* Info Banner */}
//         <div className="rounded-[28px] p-5" style={{ backgroundColor: '#E2F9D3' }}>
//           <p className="text-sm leading-relaxed" style={{ color: '#136382' }}>
//             Based on your symptoms (stomach pain, bloating, nausea), we recommend seeing these specialists:
//           </p>
//         </div>

//         {/* Specialist Cards */}
//         {specialists.map((specialist, idx) => (
//           <div
//             key={idx}
//             className="bg-white rounded-[32px] p-6 shadow-md border-2"
//             style={{
//               borderColor: idx === 0 ? '#136382' : '#D1EBEF'
//             }}
//           >
//             {/* Specialist Type */}
//             <div className="mb-4">
//               <div className="flex items-center gap-3 mb-3">
//                 <div
//                   className="w-14 h-14 rounded-[20px] flex items-center justify-center flex-shrink-0"
//                   style={{ backgroundColor: '#136382' }}
//                 >
//                   <Stethoscope className="w-8 h-8 text-white" />
//                 </div>
//                 <div className="flex-1">
//                   <h3 className="text-2xl mb-1" style={{ color: '#136382' }}>
//                     {specialist.type}
//                   </h3>
//                   <div className="flex items-center gap-2">
//                     <div
//                       className="px-3 py-1 rounded-full text-sm"
//                       style={{ backgroundColor: '#E2F9D3', color: '#136382' }}
//                     >
//                       {specialist.confidence}% match
//                     </div>
//                   </div>
//                 </div>
//               </div>

//               {/* Reason only (clean) */}
//               <div className="p-4 rounded-[20px]" style={{ backgroundColor: '#E2F9D3' }}>
//                 <p className="text-sm leading-relaxed" style={{ color: '#136382' }}>
//                   {specialist.reason}
//                 </p>
//               </div>
//             </div>

//             {/* Description */}
//             <p className="text-gray-700 mb-4 leading-relaxed">{specialist.description}</p>

//             {/* Avg Fee only */}
//             <div className="grid grid-cols-1">
//               <div className="rounded-[20px] p-4" style={{ backgroundColor: '#D1EBEF' }}>
//                 <div className="flex items-center gap-2 mb-1">
//                   <Phone className="w-4 h-4" style={{ color: '#136382' }} />
//                   <span className="text-xs text-gray-600">Avg Fee</span>
//                 </div>
//                 <p className="text-sm" style={{ color: '#136382' }}>
//                   {specialist.avgFee}
//                 </p>
//               </div>
//             </div>
//           </div>
//         ))}

//         {/* Why This Saves You Money section (kept) */}
//         <div className="bg-white rounded-[32px] p-6">
//           <h3 className="mb-3 flex items-center gap-2" style={{ color: '#136382' }}>
//             <Star className="w-6 h-6" style={{ color: '#26A68A' }} />
//             Why This Saves You Money
//           </h3>
//           <div className="space-y-2 text-sm text-gray-700 leading-relaxed">
//             <p>✓ Avoid visiting 2-3 wrong specialists (saves 3,000-6,000 PKR)</p>
//             <p>✓ Get the right diagnosis faster</p>
//             <p>✓ Reduce unnecessary tests and procedures</p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
import { useState } from 'react';
import { Stethoscope, Phone, Star, Loader2 } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;

interface Specialist {
  name: string;
  match_percentage: number;
  description: string;
  why_saves_money: string;
  avg_fee_pkr: string;
}

interface SpecialistResponse {
  summary: string;
  specialists: Specialist[];
  why_this_saves_you_money: string[];
  disclaimer: string;
}

interface SpecialistRecommenderProps {
  userInput?: string;
}

export function SpecialistRecommender({ userInput = "" }: SpecialistRecommenderProps) {
  const [input, setInput] = useState(userInput);
  const [result, setResult] = useState<SpecialistResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // If no initial userInput, show a message asking for symptoms
  if (!userInput.trim()) {
    return (
      <div className="flex flex-col h-full overflow-y-auto">
        <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
          <h2 className="text-white text-2xl">Specialist Finder</h2>
          <p className="text-white/90 text-sm mt-1">
            Describe your symptoms to find the right doctor
          </p>
        </div>
        <div className="flex-1 flex items-center justify-center px-6">
          <div className="text-center">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: '#D1EBEF' }}
            >
              <Stethoscope className="w-8 h-8" style={{ color: '#136382' }} />
            </div>
            <h3 className="mb-2" style={{ color: '#136382' }}>
              No symptoms provided
            </h3>
            <p className="text-gray-600 text-sm">
              Please go back and describe your symptoms first to get specialist recommendations
            </p>
          </div>
        </div>
      </div>
    );
  }

  const handleSubmit = async () => {
    if (!input.trim()) {
      setError("Please describe your symptoms first to find the right specialist");
      return;
    }
    
    // Check if input is too short or doesn't contain symptom keywords
    if (input.trim().length < 5) {
      setError("Please provide more detail about your symptoms");
      return;
    }
    
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${BACKEND_URL}/specialist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });

      if (!res.ok) throw new Error("Server error");
      const data: SpecialistResponse = await res.json();
      
      // Only show results if we actually got meaningful data
      if (data.specialists && data.specialists.length > 0) {
        setResult(data);
      } else {
        // Show the "no symptoms" message instead of error
        setResult({
          summary: data.summary || "No specific symptoms detected",
          specialists: [],
          why_this_saves_you_money: [],
          disclaimer: data.disclaimer || "Please describe your symptoms to get specialist recommendations."
        });
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
        <h2 className="text-white text-2xl">Specialist Finder</h2>
        <p className="text-white/90 text-sm mt-1">
          Describe your symptoms to find the right doctor
        </p>
      </div>

      {/* Input */}
      <div className="px-6 py-4 space-y-3">
        <textarea
          className="w-full rounded-[20px] p-4 text-sm border-2 resize-none outline-none"
          style={{ borderColor: '#136382', minHeight: '100px' }}
          placeholder="Describe your symptoms in English or Roman Urdu... e.g. pet mein dard hai aur ulti aa rahi hai"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          className="w-full py-3 rounded-[20px] text-white font-semibold text-sm transition-opacity disabled:opacity-50"
          style={{ backgroundColor: '#136382' }}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Finding specialists...
            </span>
          ) : "Find Specialist"}
        </button>

        {error && (
          <p className="text-red-500 text-sm text-center">{error}</p>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="px-6 pb-6 space-y-5">

          {/* Summary Banner */}
          <div className="rounded-[28px] p-5" style={{ backgroundColor: '#E2F9D3' }}>
            <p className="text-sm leading-relaxed" style={{ color: '#136382' }}>
              {result.summary}
            </p>
          </div>

          {/* No Specialists Message */}
          {result.specialists.length === 0 && (
            <div className="text-center py-8">
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                style={{ backgroundColor: '#D1EBEF' }}
              >
                <Stethoscope className="w-8 h-8" style={{ color: '#136382' }} />
              </div>
              <h3 className="mb-2" style={{ color: '#136382' }}>
                No symptoms mentioned
              </h3>
              <p className="text-gray-600 text-sm">
                Nothing to recommend. Please describe your symptoms to get specialist recommendations
              </p>
            </div>
          )}

          {/* Specialist Cards */}
          {result.specialists.map((specialist, idx) => (
            <div
              key={idx}
              className="bg-white rounded-[32px] p-6 shadow-md border-2"
              style={{ borderColor: idx === 0 ? '#136382' : '#D1EBEF' }}
            >
              <div className="mb-4">
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className="w-14 h-14 rounded-[20px] flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: '#136382' }}
                  >
                    <Stethoscope className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl mb-1" style={{ color: '#136382' }}>
                      {specialist.name}
                    </h3>
                    <div
                      className="px-3 py-1 rounded-full text-sm inline-block"
                      style={{ backgroundColor: '#E2F9D3', color: '#136382' }}
                    >
                      {specialist.match_percentage}% match
                    </div>
                  </div>
                </div>

                {/* <div className="p-4 rounded-[20px]" style={{ backgroundColor: '#E2F9D3' }}>
                  <p className="text-sm leading-relaxed" style={{ color: '#136382' }}>
                    {specialist.why_saves_money}
                  </p>
                </div> */}
              </div>

              <p className="text-gray-700 mb-4 leading-relaxed">{specialist.description}</p>

              <div className="rounded-[20px] p-4" style={{ backgroundColor: '#D1EBEF' }}>
                <div className="flex items-center gap-2 mb-1">
                  <Phone className="w-4 h-4" style={{ color: '#136382' }} />
                  <span className="text-xs text-gray-600">Avg Fee</span>
                </div>
                <p className="text-sm" style={{ color: '#136382' }}>
                  {specialist.avg_fee_pkr}
                </p>
              </div>
            </div>
          ))}

          {/* Why This Saves You Money - Only show if there are specialists */}
          {result.specialists.length > 0 && (
            <div className="bg-white rounded-[32px] p-6">
              <h3 className="mb-3 flex items-center gap-2" style={{ color: '#136382' }}>
                <Star className="w-6 h-6" style={{ color: '#26A68A' }} />
                Why This Saves You Money
              </h3>
              <div className="space-y-2 text-sm text-gray-700 leading-relaxed">
                {result.why_this_saves_you_money.map((point, idx) => (
                  <p key={idx}>✓ {point}</p>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <p className="text-xs text-center text-gray-400 px-4">
            ⚠️ {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}