import { useState } from 'react';

function App() {
  const [goal, setGoal] = useState('');
  const [output, setOutput] = useState('');

  const run = async () => {
    const res = await fetch('http://localhost:8000/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal })
    });
    const data = await res.json();
    setOutput(data.output);
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
      <pre>{output}</pre>
    </div>
  );
}

export default App;
