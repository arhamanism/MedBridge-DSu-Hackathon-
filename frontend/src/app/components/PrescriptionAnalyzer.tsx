import { useState, useRef } from 'react';
import { Upload, FileImage, Loader2, Pill, AlertCircle, CheckCircle } from 'lucide-react';

interface Medicine {
  name: string;
  dosage: string;
  frequency: string;
  indication: string;
  confidence: string;
}

interface PrescriptionResponse {
  extracted_medicines: string;
  generic_alternatives: string;
}

const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;

export function PrescriptionAnalyzer() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PrescriptionResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const analyzePrescription = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await fetch(`${BACKEND_URL}/prescription`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Server error');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Failed to analyze prescription. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-5 text-center" style={{ backgroundColor: '#136382' }}>
        <h2 className="text-white text-2xl">Prescription Analyzer</h2>
        <p className="text-white/90 text-sm mt-1">Upload prescription to find generic alternatives</p>
      </div>

      <div className="px-6 py-6 space-y-5">
        {/* Upload Area */}
        {!previewUrl && (
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="border-3 border-dashed rounded-[32px] p-8 text-center cursor-pointer transition-all hover:border-[#26A68A]"
            style={{ borderColor: '#136382', borderWidth: '3px' }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: '#D1EBEF' }}
            >
              <Upload className="w-10 h-10" style={{ color: '#136382' }} />
            </div>
            <h3 className="text-lg mb-2" style={{ color: '#136382' }}>
              Upload Prescription
            </h3>
            <p className="text-gray-500 text-sm mb-2">
              Drag and drop or click to select
            </p>
            <p className="text-gray-400 text-xs">
              Supports JPG, PNG, WEBP
            </p>
          </div>
        )}

        {/* Preview */}
        {previewUrl && (
          <div className="space-y-4">
            <div className="relative rounded-[24px] overflow-hidden border-2 border-gray-200">
              <img
                src={previewUrl}
                alt="Prescription preview"
                className="w-full max-h-64 object-contain bg-gray-50"
              />
              <button
                onClick={clearAll}
                className="absolute top-3 right-3 px-3 py-1 rounded-full bg-white shadow-md text-sm"
                style={{ color: '#136382' }}
              >
                Change Image
              </button>
            </div>

            {/* Analyze Button */}
            {!result && !loading && (
              <button
                onClick={analyzePrescription}
                className="w-full py-4 rounded-[32px] text-white text-lg font-semibold shadow-md transition-opacity hover:opacity-90"
                style={{ backgroundColor: '#136382' }}
              >
                <span className="flex items-center justify-center gap-2">
                  <FileImage className="w-6 h-6" />
                  Analyze Prescription
                </span>
              </button>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <Loader2 className="w-12 h-12 animate-spin" style={{ color: '#136382' }} />
            <p className="text-gray-500">Analyzing prescription with AI...</p>
            <p className="text-gray-400 text-sm">Extracting medicines and finding alternatives</p>
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
            {/* Extracted Medicines */}
            <div className="bg-white rounded-[32px] p-6 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-12 h-12 rounded-[16px] flex items-center justify-center"
                  style={{ backgroundColor: '#D1EBEF' }}
                >
                  <Pill className="w-6 h-6" style={{ color: '#136382' }} />
                </div>
                <h3 className="text-xl" style={{ color: '#136382' }}>
                  Extracted Medicines
                </h3>
              </div>
              <div className="p-4 rounded-[20px] bg-gray-50">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                  {result.extracted_medicines}
                </pre>
              </div>
            </div>

            {/* Generic Alternatives */}
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
                <h3 className="text-xl" style={{ color: '#136382' }}>
                  Generic Alternatives & Savings
                </h3>
              </div>
              <div className="p-4 rounded-[20px] bg-white">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {result.generic_alternatives}
                </pre>
              </div>
            </div>

            {/* Warning */}
            <div className="bg-amber-50 border border-amber-200 rounded-[20px] p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-amber-700">
                  Always consult a pharmacist or doctor before switching medications.
                  This analysis is for informational purposes only.
                </p>
              </div>
            </div>

            {/* Analyze Again */}
            <button
              onClick={clearAll}
              className="w-full py-3 rounded-[32px] border-2 text-sm font-medium transition-opacity hover:opacity-80"
              style={{ borderColor: '#136382', color: '#136382' }}
            >
              Analyze Another Prescription
            </button>
          </>
        )}
      </div>
    </div>
  );
}
