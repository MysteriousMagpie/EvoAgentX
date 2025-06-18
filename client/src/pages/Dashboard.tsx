import { useEffect, useState } from 'react';
import { getSocket } from '../socket';
import GoalInput from '../components/GoalInput';
import OutputPanel from '../components/OutputPanel';
import Loader from '../components/Loader';
import WorkflowGraph from '../components/WorkflowGraph';
import { useRunStore } from '../store/useRunStore';
import Toast from '../components/Toast';
import RunHistory from '../components/RunHistory';
import TokenBurnDownChart from '../components/TokenBurnDownChart';
import MetricsChart from '../components/MetricsChart';

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
  const [selectedRun, setSelectedRun] = useState<number | null>(1);
  const [tab, setTab] = useState<'logs' | 'tokens' | 'metrics'>('logs');

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
    <>
      {/* Left: Workflow Graph is handled by App grid */}
      <div className="hidden md:block">
        <h2 className="text-xl font-semibold mb-4">Live Workflow</h2>
        {graph && <WorkflowGraph />}
      </div>
      {/* Right: Control Panel */}
      <aside className="flex flex-col space-y-6 col-span-1">
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-2">🔍 Define Your Goal</h3>
          <GoalInput onRun={run} loading={loading} />
          <p className="text-xs text-gray-500 mt-2">Goal should be ≥ 10 characters<br />e.g. “Draft a 300-word blog post on regenerative agriculture.”</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-4 flex-1 overflow-auto">
          <h3 className="text-lg font-semibold mb-2">📜 Run History</h3>
          <RunHistory onSelect={setSelectedRun} selectedId={selectedRun} />
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-2">Run Details</h3>
          <div className="flex gap-2 mb-2">
            <button className={`px-3 py-1 rounded ${tab==='logs'?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={()=>setTab('logs')}>Logs</button>
            <button className={`px-3 py-1 rounded ${tab==='tokens'?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={()=>setTab('tokens')}>Token Burn-Down</button>
            <button className={`px-3 py-1 rounded ${tab==='metrics'?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={()=>setTab('metrics')}>Metrics</button>
          </div>
          {tab==='logs' && <OutputPanel />}
          {tab==='tokens' && <TokenBurnDownChart />}
          {tab==='metrics' && <MetricsChart />}
        </div>
      </aside>
      {loading && <Loader />}
      <Toast message={showToast ? error : ''} onClose={() => setShowToast(false)} />
    </>
  );
}
