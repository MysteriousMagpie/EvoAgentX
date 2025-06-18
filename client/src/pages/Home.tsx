import { NavLink } from 'react-router-dom';

export default function Home() {
  return (
    <div className="space-y-6 max-w-2xl mx-auto mt-12">
      <div className="flex justify-center mb-4">
        <img
          src="/assets/EAXLoGo.svg"
          alt="EvoAgentX Logo"
          className="h-24 w-auto"
          style={{ maxWidth: 160 }}
        />
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8 text-center">
        <h1 className="text-3xl font-bold mb-2">Welcome to EvoAgentX</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Your AI-powered productivity control panel.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <NavLink
            to="/dashboard"
            className="px-6 py-2 bg-primary text-white rounded font-semibold shadow hover:bg-primary/80 transition"
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/planner"
            className="px-6 py-2 bg-secondary text-white rounded font-semibold shadow hover:bg-secondary/80 transition"
          >
            Planner
          </NavLink>
        </div>
      </div>
    </div>
  );
}
