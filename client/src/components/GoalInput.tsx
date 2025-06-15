import { useState, type FormEvent } from 'react';

interface Props {
  onRun: (goal: string) => void;
  loading: boolean;
}

export default function GoalInput({ onRun, loading }: Props) {
  const [goal, setGoal] = useState('');

  const submit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!goal.trim()) return;
    onRun(goal.trim());
  };

  return (
    <form onSubmit={submit} className="flex space-x-2">
      <input
        className="flex-1 border p-2 rounded"
        placeholder="Enter your goal"
        value={goal}
        onChange={e => setGoal(e.target.value)}
      />
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded"
        type="submit"
        disabled={loading}
      >
        Run
      </button>
    </form>
  );
}
