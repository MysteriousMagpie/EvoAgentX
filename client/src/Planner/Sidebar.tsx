import React, { useState } from 'react';

const Sidebar: React.FC = () => {
  const [assistMode, setAssistMode] = useState(false);
  const [activeTab, setActiveTab] = useState('planner');

  const toggleAssistMode = () => {
    setAssistMode(!assistMode);
  };

  const navigationItems = [
    { id: 'planner', label: 'Planner', icon: '📅' },
    { id: 'backlog', label: 'Backlog', icon: '📋' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  return (
    <aside className="w-16 md:w-48 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4">
      <div className="flex-1 flex flex-col gap-4 items-center">
        {navigationItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full px-2 py-2 rounded-lg transition-colors duration-200 ${
              activeTab === item.id
                ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <div className="flex flex-col items-center gap-1">
              <span className="text-lg md:text-base">{item.icon}</span>
              <span className="text-xs md:text-sm font-medium hidden md:block">
                {item.label}
              </span>
            </div>
          </button>
        ))}
      </div>
      
      <div className="mt-auto mb-2 w-full px-2">
        <div className="flex flex-col items-center gap-2">
          <button
            onClick={toggleAssistMode}
            className={`w-full px-3 py-2 rounded-lg text-xs transition-all duration-200 ${
              assistMode
                ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 border border-green-300 dark:border-green-700'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600'
            }`}
          >
            <div className="flex flex-col items-center gap-1">
              <span className="text-lg">{assistMode ? '🤖' : '💤'}</span>
              <span className="font-medium hidden md:block">
                Assist Mode™
              </span>
              <span className="text-xs hidden md:block">
                {assistMode ? 'Active' : 'Inactive'}
              </span>
            </div>
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
