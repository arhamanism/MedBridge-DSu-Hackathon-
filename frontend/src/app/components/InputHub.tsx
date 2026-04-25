import { Mic, Search, MessageCircle, Activity, Pill, Stethoscope, ArrowRight, Loader2, AlertTriangle } from 'lucide-react';
import { useState, useRef, useCallback } from 'react';

interface InputHubProps {
  onInputSubmit: (input: string) => void;
  onModuleSelect: (module: 'symptoms' | 'decision' | 'medication' | 'specialist') => void;
  userInput: string;
}

const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;

export function InputHub({ onInputSubmit, onModuleSelect, userInput }: InputHubProps) {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingError, setRecordingError] = useState<string | null>(null);
  const [symptomWarning, setSymptomWarning] = useState<string | null>(null);
  const [hasSymptoms, setHasSymptoms] = useState(true);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const hasSubmittedInput = userInput.length > 0;

  const handleSubmit = () => {
    if (input.trim()) {
      onInputSubmit(input);
    }
  };

  const startRecording = useCallback(async () => {
    setRecordingError(null);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendAudioForTranscription(audioBlob);

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setRecordingError('Could not access microphone. Please check permissions.');
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsTranscribing(true);
    }
  }, [isRecording]);

  const sendAudioForTranscription = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await fetch(`${BACKEND_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Transcription failed');
      }

      const data = await response.json();
      const transcribedText = data.transcript || data.normalized || data.raw || '';
      
      // Check if symptoms were detected
      setHasSymptoms(data.has_symptoms !== false);
      if (data.warning) {
        setSymptomWarning(data.warning);
      } else {
        setSymptomWarning(null);
      }

      setInput(transcribedText);
      onInputSubmit(transcribedText);
    } catch (err) {
      console.error('Transcription error:', err);
      setRecordingError('Failed to transcribe audio. Please try typing instead.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const modules = [
    {
      id: 'symptoms' as const,
      title: 'Symptom Checker',
      description: 'AI diagnosis from your symptoms',
      icon: MessageCircle,
      color: '#136382'
    },
    {
      id: 'decision' as const,
      title: 'Go or Stay Home',
      description: 'Should you visit hospital?',
      icon: Activity,
      color: '#26A68A'
    },
    {
      id: 'medication' as const,
      title: 'Medication Interaction',
      description: 'Check drug safety',
      icon: Pill,
      color: '#136382'
    },
    {
      id: 'specialist' as const,
      title: 'Specialist Recommender',
      description: 'Find the right doctor',
      icon: Stethoscope,
      color: '#26A68A'
    }
  ];

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="px-6 py-6 text-center" style={{ backgroundColor: '#136382' }}>
        <h1 className="text-white text-3xl mb-2">MedBridge</h1>
        <p className="text-white/90">Your AI Healthcare Assistant</p>
      </div>

      {/* Omni-Input Area */}
      <div className="px-6 py-8 bg-white border-b border-gray-100">
        <h2 className="text-xl mb-4 text-center" style={{ color: '#136382' }}>
          {hasSubmittedInput ? 'Your Input' : 'How can we help you?'}
        </h2>

        {/* Submitted Input Display */}
        {hasSubmittedInput ? (
          <div className="p-5 rounded-[24px] mb-4" style={{ backgroundColor: '#E2F9D3' }}>
            <p className="text-base" style={{ color: '#136382' }}>
              "{userInput}"
            </p>
            <button
              onClick={() => onInputSubmit('')}
              className="text-sm mt-2 underline"
              style={{ color: '#136382' }}
            >
              Clear & start new query
            </button>
          </div>
        ) : (
          <>
            {/* Text Input with Submit */}
            <div className="relative mb-4">
              <div className="flex items-center gap-3 bg-gray-50 rounded-[28px] px-5 py-4 border-2 border-transparent focus-within:border-[#26A68A] transition-all">
                <Search className="w-6 h-6 text-gray-400" />
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                  placeholder="Type symptoms: 'pet mein dard hai' or 'stomach pain'"
                  className="flex-1 bg-transparent outline-none text-base"
                />
                {input.trim() && (
                  <button onClick={handleSubmit}>
                    <ArrowRight className="w-6 h-6" style={{ color: '#26A68A' }} />
                  </button>
                )}
              </div>
            </div>

            <div className="text-center text-sm text-gray-500 mb-4">OR</div>

            {/* Error Display */}
            {recordingError && (
              <div className="mb-4 p-4 rounded-[20px] bg-red-50 border border-red-200 text-red-600 text-sm text-center">
                {recordingError}
              </div>
            )}

            {/* Transcribing State */}
            {isTranscribing && (
              <div className="mb-4 p-4 rounded-[24px] flex items-center justify-center gap-3" style={{ backgroundColor: '#E2F9D3' }}>
                <Loader2 className="w-5 h-5 animate-spin" style={{ color: '#136382' }} />
                <span className="text-sm" style={{ color: '#136382' }}>
                  Transcribing with Whisper AI...
                </span>
              </div>
            )}

            {/* Microphone Button */}
            {!isTranscribing && (
              <button
                onClick={() => {
                  if (isRecording) {
                    stopRecording();
                  } else {
                    startRecording();
                  }
                }}
                className="w-full flex items-center justify-center gap-3 px-6 py-5 rounded-[28px] transition-all shadow-md"
                style={{ backgroundColor: isRecording ? '#26A68A' : '#136382' }}
              >
                <Mic className="w-7 h-7 text-white" />
                <span className="text-white text-lg">
                  {isRecording ? 'Recording... (Tap to stop)' : 'Voice Input - Speak Now'}
                </span>
              </button>
            )}

            {isRecording && (
              <div className="mt-4 p-4 rounded-[24px] flex items-center gap-3" style={{ backgroundColor: '#E2F9D3' }}>
                <div className="flex gap-1">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="w-1 h-8 rounded-full animate-pulse"
                      style={{
                        backgroundColor: '#26A68A',
                        animationDelay: `${i * 0.15}s`
                      }}
                    />
                  ))}
                </div>
                <span className="text-sm" style={{ color: '#136382' }}>
                  Listening...
                </span>
              </div>
            )}

            {/* Symptom Warning - No symptoms detected */}
            {symptomWarning && !hasSymptoms && (
              <div className="mt-4 p-4 rounded-[24px] border-2" style={{ backgroundColor: '#FFF3CD', borderColor: '#FFA500' }}>
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-6 h-6 text-orange-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-orange-700 mb-1">
                      No symptoms detected
                    </p>
                    <p className="text-sm text-orange-600">
                      {symptomWarning}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Module Selection - Only show after input submitted */}
      {hasSubmittedInput && (
        <div className="px-6 py-6">
          <h3 className="mb-4 text-center" style={{ color: '#136382' }}>Choose a Module</h3>
          <div className="grid grid-cols-1 gap-4">
            {modules.map((module) => {
              const Icon = module.icon;
              return (
                <button
                  key={module.id}
                  onClick={() => onModuleSelect(module.id)}
                  className="flex items-center gap-4 p-5 rounded-[28px] bg-white border-2 border-gray-100 hover:border-[#26A68A] transition-all text-left shadow-sm hover:shadow-md"
                >
                  <div
                    className="w-14 h-14 rounded-[20px] flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: module.color }}
                  >
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg mb-1" style={{ color: '#136382' }}>
                      {module.title}
                    </h4>
                    <p className="text-sm text-gray-600">{module.description}</p>
                  </div>
                  <ArrowRight className="w-6 h-6 text-gray-400" />
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Instruction when no input */}
      {!hasSubmittedInput && (
        <div className="px-6 py-8">
          <div className="text-center">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: '#D1EBEF' }}
            >
              <MessageCircle className="w-8 h-8" style={{ color: '#136382' }} />
            </div>
            <h3 className="mb-2" style={{ color: '#136382' }}>
              Enter your symptoms
            </h3>
            <p className="text-gray-600 text-sm">
              Type or speak your health concerns, then choose which tool you'd like to use
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
