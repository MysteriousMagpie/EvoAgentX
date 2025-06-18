import React from 'react';

const DatePicker: React.FC = () => (
  <header className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center justify-between">
    {/* TODO: Add compact calendar and date navigation */}
    <h2 className="text-lg font-semibold">Today</h2>
    <button className="text-sm text-blue-600">Jump to Date</button>
  </header>
);

export default DatePicker;
