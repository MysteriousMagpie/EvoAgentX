import React from 'react';

const AssistModeToggle: React.FC<{ enabled: boolean; onToggle: () => void }> = ({ enabled, onToggle }) => (
  <div className="flex items-center gap-2">
    <span className="text-xs">EvoAgentX Assist Mode™</span>
    <button
      className={`w-10 h-5 flex items-center bg-gray-300 dark:bg-gray-700 rounded-full p-1 transition-colors ${enabled ? 'bg-blue-600' : ''}`}
      onClick={onToggle}
      aria-pressed={enabled}
    >
      <span
        className={`bg-white dark:bg-gray-900 w-4 h-4 rounded-full shadow transform transition-transform ${enabled ? 'translate-x-5' : ''}`}
      />
    </button>
  </div>
);

export default AssistModeToggle;
