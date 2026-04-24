import { Plus, X, AlertTriangle, CheckCircle, Loader2, Upload, Camera, Pill, FileImage, ArrowRight } from 'lucide-react';
import { useState, useRef } from 'react';

interface Interaction {
  drug1: string;
  drug2: string;
  risk: 'low' | 'medium' | 'high';
  description: string;
}

interface MedicationResponse {
  is_safe: boolean;
  interactions: Interaction[];
  summary: string;
  disclaimer: string;
}

interface Alternative {
  original: string;
  original_ingredient?: string;
  generic: string;
  savings_percent: number;
  original_price: string;
  generic_price: string;
}

interface AlternativesResponse {
  alternatives: Alternative[];
  total_savings: string;
  disclaimer: string;
}

const BACKEND_URL = 'http://localhost:8000';

export function MedicationChecker() {
  const [medications, setMedications] = useState<string[]>([]);
  const [newMed, setNewMed] = useState('');
  const [checked, setChecked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MedicationResponse | null>(null);
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [alternativesLoading, setAlternativesLoading] = useState(false);
  const [alternatives, setAlternatives] = useState<AlternativesResponse | null>(null);

  // Image upload states
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [extractingMeds, setExtractingMeds] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addMedication = () => {
    if (newMed.trim()) {
      setMedications([...medications, newMed.trim()]);
      setNewMed('');
      resetChecks();
    }
  };

  const removeMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
    resetChecks();
  };

  const resetChecks = () => {
    setChecked(false);
    setResult(null);
    setShowAlternatives(false);
    setAlternatives(null);
  };

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      resetChecks();
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      resetChecks();
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const extractMedicinesFromImage = async () => {
    if (!selectedImage) return;
    setExtractingMeds(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('image', selectedImage);

      const response = await fetch(`${BACKEND_URL}/extract-medicines`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Server error');

      const data = await response.json();
      if (data.medicines && data.medicines.length > 0) {
        setMedications(data.medicines);
      } else {
        setError('No medicines detected in the image. Please try another image or add manually.');
      }
    } catch (err) {
      setError('Failed to extract medicines from image. Make sure the backend is running.');
    } finally {
      setExtractingMeds(false);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const checkInteractions = async () => {
    if (medications.length < 1) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/medications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ medicines: medications }),
      });
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      setResult(data);
      setChecked(true);
      setShowAlternatives(false);
    } catch (err) {
      setError("Could not check medications. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const findAlternatives = async () => {
    if (medications.length < 1) return;
    setAlternativesLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/alternatives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ medicines: medications }),
      });
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      setAlternatives(data);
      setShowAlternatives(true);
    } catch (err) {
      setError("Could not find alternatives. Make sure the backend is running.");
    } finally {
      setAlternativesLoading(false);
    }
  };

  const isSafe = result ? result.is_safe : true;

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
        <h2 className="text-white text-2xl">Medication Checker</h2>
        <p className="text-white/90 text-sm mt-1">Upload prescription or add medicines manually</p>
      </div>

      {/* Main Content */}
      <div className="px-6 py-6 space-y-5">

        {/* Image Upload Section */}
        {!imagePreview ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="border-3 border-dashed rounded-[32px] p-6 text-center cursor-pointer transition-all hover:border-[#26A68A]"
            style={{ borderColor: '#136382', borderWidth: '3px' }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
            />
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3"
              style={{ backgroundColor: '#D1EBEF' }}
            >
              <Camera className="w-8 h-8" style={{ color: '#136382' }} />
            </div>
            <h3 className="text-lg mb-1" style={{ color: '#136382' }}>
              Upload Prescription
            </h3>
            <p className="text-gray-500 text-sm">
              Drag & drop or click to select image
            </p>
            <p className="text-gray-400 text-xs mt-1">
              Auto-extract medicines from prescription
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="relative rounded-[24px] overflow-hidden border-2 border-gray-200">
              <img
                src={imagePreview}
                alt="Prescription preview"
                className="w-full max-h-48 object-contain bg-gray-50"
              />
              <button
                onClick={clearImage}
                className="absolute top-3 right-3 px-3 py-1 rounded-full bg-white shadow-md text-sm"
                style={{ color: '#136382' }}
              >
                Change
              </button>
            </div>
            {medications.length === 0 && !extractingMeds && (
              <button
                onClick={extractMedicinesFromImage}
                className="w-full py-3 rounded-[24px] text-white font-medium shadow-md transition-opacity hover:opacity-90"
                style={{ backgroundColor: '#136382' }}
              >
                <span className="flex items-center justify-center gap-2">
                  <FileImage className="w-5 h-5" />
                  Extract Medicines from Image
                </span>
              </button>
            )}
            {extractingMeds && (
              <div className="flex flex-col items-center justify-center py-4 space-y-2">
                <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#136382' }} />
                <p className="text-gray-500 text-sm">Extracting medicines...</p>
              </div>
            )}
          </div>
        )}

        {/* Manual Add Medication */}
        <div className="bg-white rounded-[32px] p-6">
          <h3 className="mb-4 text-sm font-medium" style={{ color: '#136382' }}>
            Or Add Manually
          </h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={newMed}
              onChange={(e) => setNewMed(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addMedication()}
              placeholder="e.g., Panadol, Aspirin..."
              className="flex-1 px-5 py-4 rounded-[24px] bg-gray-50 text-base outline-none"
            />
            <button
              onClick={addMedication}
              className="p-4 rounded-full"
              style={{ backgroundColor: '#26A68A' }}
            >
              <Plus className="w-6 h-6 text-white" />
            </button>
          </div>
        </div>

        {/* Medication Tags */}
        {medications.length > 0 && (
          <div className="bg-white rounded-[32px] p-6">
            <h3 className="mb-4 text-sm font-medium" style={{ color: '#136382' }}>
              Your Medicines ({medications.length})
            </h3>
            <div className="flex flex-wrap gap-3">
              {medications.map((med, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 px-4 py-2 rounded-full border-2 shadow-sm"
                  style={{
                    backgroundColor: '#26A68A',
                    borderColor: '#1a7a5e'
                  }}
                >
                  <Pill className="w-4 h-4 text-white" />
                  <span className="text-white text-sm">{med}</span>
                  <button onClick={() => removeMedication(idx)} className="hover:scale-110 transition-transform">
                    <X className="w-4 h-4 text-white" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-[20px] p-4 text-red-600 text-sm text-center">
            {error}
          </div>
        )}

        {/* Check Interactions Button */}
        {medications.length >= 1 && !checked && !loading && (
          <button
            onClick={checkInteractions}
            className="w-full px-6 py-5 rounded-[28px] text-white text-xl transition-all shadow-lg"
            style={{ backgroundColor: '#136382' }}
          >
            Check Safety & Interactions
          </button>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-8 space-y-3">
            <Loader2 className="w-8 h-8 animate-spin" style={{ color: '#136382' }} />
            <p className="text-gray-500">Checking medication safety...</p>
          </div>
        )}

        {/* Safety Result */}
        {checked && result && (
          <>
            {/* No Medicines Detected Case */}
            {result.summary === "No valid medicines detected" && (
              <div className="text-center py-8">
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                  style={{ backgroundColor: '#D1EBEF' }}
                >
                  <Pill className="w-8 h-8" style={{ color: '#136382' }} />
                </div>
                <h3 className="mb-2" style={{ color: '#136382' }}>
                  No medicines found
                </h3>
                <p className="text-gray-600 text-sm">
                  Nothing to check. Please enter actual medicine names to check for interactions
                </p>
              </div>
            )}

            {/* Normal Result Case */}
            {result.summary !== "No valid medicines detected" && (
              <>
                <div
                  className="rounded-[32px] p-6 shadow-lg border-4"
                  style={{
                    backgroundColor: isSafe ? '#26A68A' : '#d4183d',
                    borderColor: isSafe ? '#1a7a5e' : '#b01530'
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg"
                      style={{
                        backgroundColor: isSafe ? '#E2F9D3' : '#ffe0e0'
                      }}
                    >
                      {isSafe ? (
                        <CheckCircle className="w-10 h-10" style={{ color: '#26A68A' }} />
                      ) : (
                        <AlertTriangle className="w-10 h-10 text-red-500" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-2xl text-white mb-1">
                        {isSafe ? 'SAFE TO TAKE' : 'WARNING - INTERACTIONS FOUND'}
                      </h3>
                      <p className="text-white/90 text-sm">
                        {result.summary}
                      </p>
                    </div>
                  </div>
                </div>

            {/* Interaction Details */}
                {result.interactions.length > 0 && (
                  <div className="bg-white rounded-[32px] p-6">
                    <h3 className="mb-4" style={{ color: '#136382' }}>Interaction Details</h3>
                    <div className="space-y-3">
                      {result.interactions.map((interaction, idx) => (
                        <div
                          key={idx}
                          className="p-4 rounded-[24px] border-l-4"
                          style={{
                            backgroundColor: interaction.risk === 'high' ? '#ffe0e0' :
                              interaction.risk === 'medium' ? '#fff4e0' : '#E2F9D3',
                            borderColor: interaction.risk === 'high' ? '#d4183d' :
                              interaction.risk === 'medium' ? '#FFA500' : '#26A68A'
                          }}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium" style={{ color: '#136382' }}>
                              {interaction.drug1} + {interaction.drug2}
                            </span>
                            <span
                              className="px-3 py-1 rounded-full text-xs uppercase tracking-wide text-white"
                              style={{
                                backgroundColor: interaction.risk === 'high' ? '#d4183d' :
                                  interaction.risk === 'medium' ? '#FFA500' : '#26A68A'
                              }}
                            >
                              {interaction.risk} risk
                            </span>
                          </div>
                          <p className="text-sm text-gray-700">{interaction.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Find Alternatives Button - Only shows after safety check */}
                {!showAlternatives && !alternativesLoading && (
                  <button
                    onClick={findAlternatives}
                    className="w-full px-6 py-4 rounded-[28px] border-2 text-lg font-medium transition-all"
                    style={{ borderColor: '#26A68A', color: '#26A68A' }}
                  >
                    <span className="flex items-center justify-center gap-2">
                      Find Generic Alternatives
                      <ArrowRight className="w-5 h-5" />
                    </span>
                  </button>
                )}

                {/* Alternatives Loading */}
                {alternativesLoading && (
                  <div className="flex flex-col items-center justify-center py-6 space-y-2">
                    <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#26A68A' }} />
                    <p className="text-gray-500 text-sm">Finding cheaper alternatives...</p>
                  </div>
                )}

                {/* Alternatives Result */}
                {showAlternatives && alternatives && (
                  <>
                    {alternatives.alternatives.length === 0 ? (
                      /* No alternatives found - already generic */
                      <div
                        className="rounded-[32px] p-6 shadow-sm border-2"
                        style={{ backgroundColor: '#D1EBEF', borderColor: '#136382' }}
                      >
                        <div className="flex items-center gap-3 mb-4">
                          <div
                            className="w-12 h-12 rounded-[16px] flex items-center justify-center"
                            style={{ backgroundColor: '#136382' }}
                          >
                            <CheckCircle className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h3 className="text-xl" style={{ color: '#136382' }}>
                              Already Using Generics!
                            </h3>
                            <p className="text-sm text-gray-600">
                              Your medicines are already cost-effective options.
                            </p>
                          </div>
                        </div>
                        <p className="text-sm text-gray-500 text-center">
                          {alternatives.disclaimer}
                        </p>
                      </div>
                    ) : (
                      /* Alternatives found */
                      <div
                        className="rounded-[32px] p-6 shadow-sm border-2"
                        style={{ backgroundColor: '#E2F9D3', borderColor: '#26A68A' }}
                      >
                        <div className="flex items-center gap-3 mb-4">
                          <div
                            className="w-12 h-12 rounded-[16px] flex items-center justify-center"
                            style={{ backgroundColor: '#26A68A' }}
                          >
                            <CheckCircle className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h3 className="text-xl" style={{ color: '#136382' }}>
                              Generic Alternatives
                            </h3>
                            <p className="text-sm" style={{ color: '#26A68A' }}>
                              Total savings: {alternatives.total_savings}
                            </p>
                          </div>
                        </div>

                        <div className="space-y-3">
                          {alternatives.alternatives.map((alt, idx) => (
                            <div key={idx} className="bg-white rounded-[20px] p-4">
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-medium" style={{ color: '#136382' }}>
                                  {alt.original}
                                </span>
                                <span className="text-sm text-gray-500 line-through">
                                  {alt.original_price}
                                </span>
                              </div>
                              {alt.original_ingredient && (
                                <p className="text-xs text-gray-400 mb-2">
                                  Contains: {alt.original_ingredient}
                                </p>
                              )}
                              <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                                <span className="text-sm font-medium" style={{ color: '#26A68A' }}>
                                  {alt.generic}
                                </span>
                                <span className="font-medium" style={{ color: '#26A68A' }}>
                                  {alt.generic_price}
                                </span>
                              </div>
                              <div className="mt-2 text-xs px-2 py-1 rounded bg-green-50 inline-block" style={{ color: '#26A68A' }}>
                                Save {alt.savings_percent}%
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="mt-4 p-3 rounded-[16px] border-2 border-orange-300 bg-orange-50">
                          <div className="flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
                            <p className="text-xs text-orange-700 font-medium">
                              {alternatives.disclaimer}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}

                {/* Disclaimer */}
                <div className="p-4 rounded-[16px] border-2 border-orange-300 bg-orange-50 mx-4">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-orange-700 font-medium">
                      {result.disclaimer}
                    </p>
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
