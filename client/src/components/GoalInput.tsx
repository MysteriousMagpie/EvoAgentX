import { useState } from 'react';

interface Props {
  onRun: (goal: string) => void;
  loading: boolean;
}
export default function GoalInput({ onRun, loading }: Props) {
  const [goal, setGoal] = useState('');
  return (
    <>
      <textarea
        className="w-full p-3 rounded border"
        rows={3}
        value={goal}
        onChange={e => setGoal(e.target.value)}
        placeholder="Enter goal"
      />
      <button
        onClick={() => onRun(goal)}
        disabled={!goal || loading}
        className="mt-2 px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-40"
      >
        {loading ? 'Running…' : 'Run'}
      </button>
    </>
  );
}
