import { NavLink } from 'react-router-dom';

export default function Navbar({ darkMode, setDarkMode }: { darkMode: boolean, setDarkMode: (v: boolean) => void }) {
  return (
    <nav className="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-8 py-3 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="font-bold text-xl tracking-tight text-primary">EvoAgentX</span>
        <NavLink to="/" className="ml-6 text-gray-700 dark:text-gray-200 hover:text-primary">Agent Hub</NavLink>
        <NavLink to="/planner" className="ml-4 text-gray-700 dark:text-gray-200 hover:text-primary">Planner</NavLink>
        <NavLink to="/runs" className="ml-4 text-gray-700 dark:text-gray-200 hover:text-primary">Runs</NavLink>
      </div>
      <div className="flex items-center gap-4">
        <button
          aria-label="Toggle dark mode"
          className="rounded p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m8.66-13.66l-.71.71M4.05 19.07l-.71.71M21 12h-1M4 12H3m16.66 4.66l-.71-.71M4.05 4.93l-.71-.71" /></svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-700 dark:text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z" /></svg>
          )}
        </button>
      </div>
    </nav>
  );
}
