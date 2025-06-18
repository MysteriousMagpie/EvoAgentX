import React from 'react';
import DatePicker from './DatePicker';
import Timeline from './Timeline';
import SuggestedTasksPanel from './SuggestedTasksPanel';

const MainPanel: React.FC = () => (
  <main className="flex-1 flex flex-col">
    <DatePicker />
    <div className="flex flex-1 overflow-hidden">
      <Timeline />
      <SuggestedTasksPanel />
    </div>
  </main>
);

export default MainPanel;
