import { useState } from 'react';
import { MessageCircle, Activity, Pill, Stethoscope } from 'lucide-react';
import { InputHub } from './components/InputHub';
import { SymptomChecker } from './components/SymptomChecker';
import { DecisionEngine } from './components/DecisionEngine';
import { MedicationChecker } from './components/MedicationChecker';
import { SpecialistRecommender } from './components/SpecialistRecommender';

type ModuleType = 'symptoms' | 'decision' | 'medication' | 'specialist' | null;

export default function App() {
  const [activeModule, setActiveModule] = useState<ModuleType>(null);
  const [userInput, setUserInput] = useState('');

  const handleInputSubmit = (input: string) => {
    setUserInput(input);
    if (!input) {
      setActiveModule(null); // Reset when clearing input
    }
  };

  const tabs = [
    { id: 'symptoms' as const, label: 'Symptoms', icon: MessageCircle },
    { id: 'decision' as const, label: 'Decision', icon: Activity },
    { id: 'medication' as const, label: 'Meds', icon: Pill },
    { id: 'specialist' as const, label: 'Specialist', icon: Stethoscope }
  ];

  const renderModule = () => {
    if (!userInput) {
      return (
        <div className="flex items-center justify-center h-full px-6 text-center">
          <div>
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: '#D1EBEF' }}
            >
              <MessageCircle className="w-10 h-10" style={{ color: '#136382' }} />
            </div>
            <h3 className="text-xl mb-2" style={{ color: '#136382' }}>
              Enter Your Symptoms
            </h3>
            <p className="text-gray-600">
              Use the input area on the left to describe your health concerns
            </p>
          </div>
        </div>
      );
    }

    if (!activeModule) {
      return (
        <div className="flex items-center justify-center h-full px-6 text-center">
          <div>
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: '#E2F9D3' }}
            >
              <Activity className="w-10 h-10" style={{ color: '#26A68A' }} />
            </div>
            <h3 className="text-xl mb-2" style={{ color: '#136382' }}>
              Select a Module
            </h3>
            <p className="text-gray-600">
              Choose a health module from the left to analyze your symptoms
            </p>
          </div>
        </div>
      );
    }

    switch (activeModule) {
      case 'symptoms':
        return <SymptomChecker userInput={userInput} />;
      case 'decision':
        return <DecisionEngine userInput={userInput} />;
      case 'medication':
        return <MedicationChecker />;
      case 'specialist':
        return <SpecialistRecommender userInput={userInput} />;
    }
  };

  return (
    <div className="size-full" style={{ backgroundColor: '#F4F9FF' }}>
      {/* Full Width Layout (Both Mobile and Desktop) */}
      <div className="flex flex-col h-full">
        {/* Input Hub at Top (Collapsible when module selected) */}
        {activeModule === null && (
          <div className="flex-1 overflow-y-auto">
            <InputHub
              onInputSubmit={handleInputSubmit}
              onModuleSelect={setActiveModule}
              userInput={userInput}
            />
          </div>
        )}

        {/* Results Below */}
        {activeModule !== null && (
          <div className="flex-1 overflow-hidden">
            {renderModule()}
          </div>
        )}

        {/* Bottom Navigation */}
        {activeModule !== null && (
          <div className="bg-white border-t border-gray-200 px-2 py-3 shadow-lg">
            <div className="flex items-center justify-around">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeModule === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveModule(tab.id)}
                    className="flex flex-col items-center gap-1 px-3 py-2 rounded-[20px] transition-all min-w-[70px]"
                    style={{
                      backgroundColor: isActive ? '#D1EBEF' : 'transparent'
                    }}
                  >
                    <Icon
                      className="w-6 h-6"
                      style={{ color: isActive ? '#136382' : '#9CA3AF' }}
                    />
                    <span
                      className="text-xs"
                      style={{ color: isActive ? '#136382' : '#9CA3AF' }}
                    >
                      {tab.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Back to Modules Button */}
        {activeModule !== null && userInput && (
          <button
            onClick={() => setActiveModule(null)}
            className="absolute top-4 left-4 px-4 py-2 rounded-full bg-white shadow-lg border border-gray-200 text-sm z-10"
            style={{ color: '#136382' }}
          >
            ← Back to Modules
          </button>
        )}
      </div>
    </div>
  );
}