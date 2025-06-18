import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Dashboard from './pages/Dashboard';
import Planner from './pages/Planner';
import { getSocket } from './socket';

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    const socket = getSocket();
    socket.on('connect', () => {
      console.log('Connected to Socket.IO server');
    });
    socket.on('disconnect', () => {
      console.log('Disconnected from Socket.IO server');
    });
    socket.on('progress', (message) => {
      console.log('Progress event:', message);
    });
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('progress');
    };
  }, []);

  return (
    <BrowserRouter>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      <div className="grid grid-cols-3 gap-6 p-8 pt-12 bg-gray-50 dark:bg-gray-950 min-h-screen">
        {/* Left: Workflow Graph */}
        <section className="col-span-2 bg-white dark:bg-gray-900 rounded-lg shadow p-4 min-h-[600px]">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/planner" element={<Planner />} />
            {/* <Route path="/runs" element={<History />} /> */}
          </Routes>
        </section>
        {/* Right: Control Panel */}
        <aside className="flex flex-col space-y-6">
          {/* The right pane content will be handled in Dashboard */}
        </aside>
      </div>
    </BrowserRouter>
  );
}

