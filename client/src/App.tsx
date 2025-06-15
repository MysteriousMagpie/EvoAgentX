import { useState } from 'react';
import OutputPanel from './components/OutputPanel';
import Loader from './components/Loader';

function App() {
  const [goal, setGoal] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true);
    setError('');
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
      <textarea
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        placeholder="Enter goal"
        rows={4}
        cols={60}
      />
      <br />
      <button onClick={run}>Run</button>
      <OutputPanel output={output} />
      {loading && <Loader />}
      {error && <p className="text-red-600 mt-2">{error}</p>}
      <pre>{output}</pre>
    </div>
  );
}

export default App;
