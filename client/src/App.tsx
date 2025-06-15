import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './Dashboard';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        {/* sidebar */}
        <nav className="w-52 border-r p-4 space-y-2">
          <NavLink to="/" className="block">Agent Hub</NavLink>
          {/* future links */}
        </nav>

        {/* main */}
        <div className="flex-1 p-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* <Route path="/history" element={<History />} /> */}
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
