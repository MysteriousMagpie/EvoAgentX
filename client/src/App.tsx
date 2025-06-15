import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Planner from './pages/Planner';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        {/* sidebar */}
        <nav className="w-52 border-r p-4 space-y-2">
          <NavLink to="/" className="block">Agent Hub</NavLink>
          <NavLink to="/planner" className="block">Planner</NavLink>
        </nav>

        {/* main */}
        <div className="flex-1 p-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/planner" element={<Planner />} />
            {/* <Route path="/history" element={<History />} /> */}
          </Routes>
        </div>
      </div>
    </BrowserRouter>

  );
}
