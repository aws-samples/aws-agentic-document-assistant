import React, { useEffect, useState } from 'react';

interface DebugToggleSwitchProps {
  onToggle: (value: boolean) => void;
}

const DebugToggleSwitch: React.FC<DebugToggleSwitchProps> = ({ onToggle }) => {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const debugMode = localStorage.getItem('debugMode');
    setEnabled(debugMode === 'true');
  }, []);

  const toggleSwitch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.checked;
    localStorage.setItem('debugMode', String(value));
    setEnabled(value);
    onToggle(value);
  };

  return (
    <label className="flex text-gray-600 text-sm hover:text-gray-800 items-center space-x-3">
      <input
        type="checkbox"
        checked={enabled}
        onChange={toggleSwitch}
        className="form-checkbox h-4 w-4 rounded"
      />
      <span>Debug Mode</span>
    </label>
  );
};

export default DebugToggleSwitch;