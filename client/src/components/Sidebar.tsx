import { NavLink } from 'react-router-dom';

export default function Sidebar({ darkMode, setDarkMode }: { darkMode: boolean; setDarkMode: (v: boolean) => void }) {
  return (
    <aside className="hidden md:flex fixed inset-y-0 left-0 w-64 bg-gray-800 dark:bg-gray-900 text-gray-100 flex flex-col justify-between">
      <div className="p-6">
        {/* Logo removed to prevent blocking content */}
        <nav className="space-y-2">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `block px-4 py-2 rounded hover:bg-gray-700 ${isActive ? 'bg-primary text-white' : 'text-gray-100'}`
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `block px-4 py-2 rounded hover:bg-gray-700 ${isActive ? 'bg-primary text-white' : 'text-gray-100'}`
            }
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/planner"
            className={({ isActive }) =>
              `block px-4 py-2 rounded hover:bg-gray-700 ${isActive ? 'bg-primary text-white' : 'text-gray-100'}`
            }
          >
            Planner
          </NavLink>
        </nav>
      </div>
      <div className="p-6">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="w-full flex items-center justify-center px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
        >
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </aside>
  );
}
