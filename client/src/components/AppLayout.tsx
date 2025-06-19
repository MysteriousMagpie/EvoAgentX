import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface AppLayoutProps {
  children: ReactNode;
  darkMode: boolean;
  setDarkMode: (v: boolean) => void;
}

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: '📊' },
  { name: 'Planner', path: '/planner', icon: '🗺️' },
  // Add more nav items as needed
];

export default function AppLayout({ children, darkMode, setDarkMode }: AppLayoutProps) {
  const location = useLocation();
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-800 shadow flex flex-col justify-between">
        <div>
          <div className="p-6 flex items-center gap-2">
            <img src="/assets/EAXLoGo.svg" alt="EvoAgentX Logo" className="h-8 w-8" />
            <span className="font-bold text-lg text-primary">EvoAgentX</span>
          </div>
          <nav className="mt-8 space-y-2">
            {navItems.map(item => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-colors font-medium ${location.pathname === item.path ? 'bg-primary text-white' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'}`}
              >
                <span>{item.icon}</span> {item.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="flex items-center gap-2 px-3 py-2 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            {darkMode ? '🌙 Dark' : '☀️ Light'}
          </button>
          <span className="text-xs text-gray-400">v1.0</span>
        </div>
      </aside>
      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white dark:bg-gray-900 shadow flex items-center px-8">
          <h1 className="text-2xl font-semibold text-gray-800 dark:text-gray-100">Dashboard</h1>
          {/* Add user info, notifications, etc. here */}
        </header>
        <section className="flex-1 p-8 overflow-y-auto">{children}</section>
      </main>
    </div>
  );
}
