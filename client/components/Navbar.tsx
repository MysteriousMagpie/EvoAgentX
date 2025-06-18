import React from "react";

const Navbar: React.FC = () => {
  return (
    <nav className="bg-gray-800 p-4 text-white flex items-center justify-between">
      <div className="text-xl font-bold">EvoAgentX</div>
      <ul className="flex space-x-4">
        <li><a href="/" className="hover:underline">Home</a></li>
        <li><a href="/dashboard" className="hover:underline">Dashboard</a></li>
        <li><a href="/planner" className="hover:underline">Planner</a></li>
      </ul>
    </nav>
  );
};

export default Navbar;
