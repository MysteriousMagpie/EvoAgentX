// Entry point for Planner UI
import React from 'react';
import MainPanel from './MainPanel';

const Planner: React.FC = () => (
  <div className="flex h-screen bg-gray-100 dark:bg-gray-900 pt-16 md:pl-64">
    <MainPanel />
  </div>
);

export default Planner;
