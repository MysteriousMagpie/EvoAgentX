import { useEffect, useState } from 'react';
import { getSocket } from '../socket';
import GoalInput from '../components/GoalInput';
import OutputPanel from '../components/OutputPanel';
import Loader from '../components/Loader';
import { useRunStore } from '../store/useRunStore';
import Toast from '../components/Toast';
import RunHistory from '../components/RunHistory';
import TokenBurnDownChart from '../components/TokenBurnDownChart';
import MetricsChart from '../components/MetricsChart';
import { API_URL } from '../api';

export default function Dashboard() {
  const {
    loading,
    error,
    setLoading,
    setError,
    addProgress,
    setOutput,
    setTokenUsage,
    setActiveTask,
    reset,
    runs,
    fetchRuns,
    saveRun,
    loadRuns,
    tokenUsage
  } = useRunStore();

  const [showToast, setShowToast] = useState(false);
  const [selectedRun, setSelectedRun] = useState<number | null>(1);
  const [tab, setTab] = useState<'logs' | 'tokens' | 'metrics'>('logs');

  useEffect(() => {
    loadRuns();
  }, []);

  useEffect(() => {
    if (error) setShowToast(true);
  }, [error]);

  useEffect(() => {
    const socket = getSocket();
    const onProgress = (data: string) => addProgress(data);
    const onOutput = (data: string) => setOutput(data);
    const onTokenUsage = (usage: number) => setTokenUsage(usage);
    const onActiveTask = (task: string) => setActiveTask(task);
    const onError = (msg: string) => setError(msg);

    socket.on('progress', onProgress);
    socket.on('output', onOutput);
    socket.on('token_usage', onTokenUsage);
    socket.on('active_task', onActiveTask);
    socket.on('error', onError);

    return () => {
      socket.off('progress', onProgress);
      socket.off('output', onOutput);
      socket.off('token_usage', onTokenUsage);
      socket.off('active_task', onActiveTask);
      socket.off('error', onError);
    };
  }, [addProgress, setOutput, setTokenUsage, setActiveTask, setError, loadRuns]);

  // Load run history
  useEffect(() => {
    void fetchRuns();
  }, [fetchRuns]);

  const run = async (goal: string) => {
    setLoading(true);
    setError('');
    reset();
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal })
      });
      if (!res.ok) {
        let msg = `Status ${res.status}`;
        try {
          const data = await res.json();
          if (data && data.detail && typeof data.detail === 'string') {
            msg = data.detail;
          }
        } catch {}
        setError(msg);
        setLoading(false);
        return;
      }
      // Save run to history
      const now = new Date();
      saveRun({
        id: now.getTime(),
        goal,
        status: '✅',
        tokens: tokenUsage ?? 0,
        cost: 0,
        time: now.toLocaleString()
      });
      setLoading(false);
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto mt-8">
      {/* Define Your Goal Section */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">🔍 Define Your Goal</h2>
        <GoalInput onRun={run} loading={loading} />
        <p className="text-sm text-gray-500 mt-2">Goal should be ≥ 10 characters<br />e.g. “Draft a 300-word blog post on regenerative agriculture.”</p>
      </div>
      {/* Run History Section */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 overflow-auto">
        <h2 className="text-xl font-semibold mb-4">📜 Run History</h2>
        <RunHistory runs={runs} onSelect={setSelectedRun} selectedId={selectedRun} />
      </div>
      {/* Run Details Section */}
      {selectedRun !== null && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">⚙️ Run Details</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            <button className={`px-4 py-2 rounded ${tab==='logs'?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={()=>setTab('logs')}>Logs</button>
            <button className={`px-4 py-2 rounded ${tab==='tokens'?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={()=>setTab('tokens')}>Token Burn-Down</button>
            <button className={`px-4 py-2 rounded ${tab==='metrics'?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={()=>setTab('metrics')}>Metrics</button>
          </div>
          {tab==='logs' && <OutputPanel />}
          {tab==='tokens' && <TokenBurnDownChart />}
          {tab==='metrics' && <MetricsChart />}
        </div>
      )}
      {loading && <Loader />}
      <Toast message={showToast ? error : ''} onClose={() => setShowToast(false)} />
    </div>
  );
}
