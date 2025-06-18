import { useState } from 'react';

const mockRuns = [
  { id: 1, goal: 'Draft a 300-word blog post on regenerative agriculture.', status: '✅', tokens: 1200, cost: 0.12, time: '2025-06-17 10:12' },
  { id: 2, goal: 'Summarize the latest AI research.', status: '❌', tokens: 800, cost: 0.08, time: '2025-06-16 15:40' },
  { id: 3, goal: 'Write a poem about mushrooms.', status: '✅', tokens: 600, cost: 0.06, time: '2025-06-15 09:22' },
];

export default function RunHistory({ onSelect, selectedId }: { onSelect: (id: number) => void, selectedId: number | null }) {
  return (
    <ul className="divide-y divide-gray-200 dark:divide-gray-800">
      {mockRuns.map(run => (
        <li
          key={run.id}
          className={`py-2 px-2 rounded cursor-pointer flex items-center justify-between transition-colors ${selectedId === run.id ? 'bg-primary/10 dark:bg-primary/20' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}`}
          onClick={() => onSelect(run.id)}
        >
          <div>
            <div className="font-medium text-sm text-gray-900 dark:text-gray-100 truncate max-w-[180px]">{run.goal}</div>
            <div className="text-xs text-gray-500">{run.time}</div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">{run.status}</span>
            <span className="text-xs text-gray-400">{run.tokens}T</span>
            <span className="text-xs text-gray-400">${run.cost.toFixed(2)}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}
