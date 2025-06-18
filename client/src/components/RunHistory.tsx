import type { RunRecord } from '../store/useRunStore';

interface RunHistoryProps {
  runs: RunRecord[];
  onSelect: (id: number) => void;
  selectedId: number | null;
}
export default function RunHistory({ runs, onSelect, selectedId }: RunHistoryProps) {
  return (
    <ul className="divide-y divide-gray-200 dark:divide-gray-800">
      {runs.map(run => (
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
