import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import Home from './pages/Home';
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
      <AppLayout darkMode={darkMode} setDarkMode={setDarkMode}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/planner" element={<Planner />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

