import React from 'react';

const Sidebar: React.FC = () => (
  <aside className="w-16 md:w-48 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4">
    {/* TODO: Add navigation links and Assist Mode toggle */}
    <div className="flex-1 flex flex-col gap-4 items-center">
      <button className="text-xs md:text-base font-bold">Planner</button>
      <button className="text-xs md:text-base">Backlog</button>
      <button className="text-xs md:text-base">Settings</button>
    </div>
    <div className="mt-auto mb-2">
      {/* Assist Mode Toggle placeholder */}
      <span className="text-xs text-gray-500">Assist Mode™</span>
    </div>
  </aside>
);

export default Sidebar;
