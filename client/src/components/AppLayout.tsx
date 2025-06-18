import React from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children, darkMode, setDarkMode }: AppLayoutProps & { darkMode: boolean; setDarkMode: (v: boolean) => void }) {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      {/* Mobile top nav */}
      <div className="md:hidden w-full fixed top-0 z-40">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      </div>
      {/* Sidebar for md+ screens */}
      <Sidebar darkMode={darkMode} setDarkMode={setDarkMode} />
      <main className="flex-1 pt-16 md:pt-0 p-6 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
