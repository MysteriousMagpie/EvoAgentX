import { useEffect, useState } from 'react';
import GoalInput from '../components/GoalInput';
import OutputPanel from '../components/OutputPanel';
import Loader from '../components/Loader';
import WorkflowGraph from '../components/WorkflowGraph';
import { useRunStore } from '../store/useRunStore';
import { getSocket } from '../socket';
import Toast from '../components/Toast';

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
    setActiveTask,
    reset
  } = useRunStore();
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    if (error) setShowToast(true);
  }, [error]);

  useEffect(() => {
    const socket = getSocket();
    const onProgress = (data: string) => addProgress(data);
    const onOutput = (data: string) => setOutput(data);
    const onGraph = (data: any) => setGraph(data);
    const onTokenUsage = (usage: number) => setTokenUsage(usage);
    const onActiveTask = (task: string) => setActiveTask(task);
    const onError = (msg: string) => setError(msg);

    socket.on('progress', onProgress);
    socket.on('output', onOutput);
    socket.on('graph', onGraph);
    socket.on('token_usage', onTokenUsage);
    socket.on('active_task', onActiveTask);
    socket.on('error', onError);

    return () => {
      socket.off('progress', onProgress);
      socket.off('output', onOutput);
      socket.off('graph', onGraph);
      socket.off('token_usage', onTokenUsage);
      socket.off('active_task', onActiveTask);
      socket.off('error', onError);
    };
  }, [addProgress, setOutput, setGraph, setTokenUsage, setActiveTask, setError]);

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
      // No need to set output/graph here, will be handled by socket events
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
      <Toast message={showToast ? error : ''} onClose={() => setShowToast(false)} />
    </div>
  );
}
