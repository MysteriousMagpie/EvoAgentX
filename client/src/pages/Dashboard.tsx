import { useState, useEffect } from 'react';
import GoalInput from '../components/GoalInput';
import OutputPanel from '../components/OutputPanel';
import Loader from '../components/Loader';

export default function Dashboard() {
  const [output, setOutput] = useState('');
  const [progress, setProgress] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = ev => setProgress(prev => [...prev, ev.data]);
    return () => ws.close();
  }, []);

  const run = async (goal: string) => {
    setLoading(true);
    setError('');
    setProgress([]);
    try {
      const res = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal })
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();
      setOutput(data.output);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h1>EvoAgentX</h1>
      <GoalInput onRun={run} loading={loading} />
      <OutputPanel output={output} progress={progress} />
      {loading && <Loader />}
      {error && <p className="text-red-600 mt-2">{error}</p>}
    </div>
  );
}
