import React from 'react';

const SuggestedTasksPanel: React.FC = () => (
  <aside className="w-64 max-w-xs bg-white dark:bg-gray-800 p-4 border-l border-gray-200 dark:border-gray-700 flex flex-col">
    {/* TODO: List suggested tasks, Add/Refine buttons */}
    <h3 className="font-semibold mb-2">Suggested Tasks (AI zone)</h3>
    <div className="flex-1 flex flex-col gap-2 text-gray-500">
      <span>No suggestions yet.</span>
    </div>
    <div className="mt-4 flex gap-2">
      <button className="bg-blue-600 text-white px-3 py-1 rounded">Add to Plan</button>
      <button className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-1 rounded">Refine</button>
    </div>
  </aside>
);

export default SuggestedTasksPanel;
