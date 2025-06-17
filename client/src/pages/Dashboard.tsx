import { useEffect } from 'react';
import { io } from 'socket.io-client';
import GoalInput from '../components/GoalInput';
import OutputPanel from '../components/OutputPanel';
import Loader from '../components/Loader';
import WorkflowGraph from '../components/WorkflowGraph';
import { useRunStore } from '../store/useRunStore';

export default function Dashboard() {
  const {
    loading,
    error,
    graph,
    setLoading,
    setError,
    addProgress,
    setOutput,
    setGraph,
    setTokenUsage,
    reset
  } = useRunStore();

  useEffect(() => {
    const socket = io('http://localhost:8000'); // Adjust port if needed
    socket.on('connect', () => {
      console.log('🟢 Socket.IO connected:', socket.id);
    });
    socket.on('progress', (data: string) => {
      addProgress(data);
    });
    return () => { socket.disconnect(); };
  }, [addProgress]);

  const run = async (goal: string) => {
    setLoading(true);
    setError('');
    reset();
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal })
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();
      setOutput(data.output);
      setGraph(data.graph);
      if (data.token_usage) setTokenUsage(data.token_usage);
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
      {graph && <WorkflowGraph />}
      <OutputPanel />
      {loading && <Loader />}
      {error && <p className="text-red-600 mt-2">{error}</p>}
    </div>
  );
}
