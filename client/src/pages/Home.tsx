import { NavLink } from 'react-router-dom';

export default function Home() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto mt-8">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 text-center">
        <h1 className="text-3xl font-bold mb-2">Welcome to EvoAgentX</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Your AI-powered productivity control panel.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <NavLink
            to="/dashboard"
            className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/80"
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/planner"
            className="px-4 py-2 bg-secondary text-white rounded hover:bg-secondary/80"
          >
            Planner
          </NavLink>
        </div>
      </div>
    </div>
  );
}
