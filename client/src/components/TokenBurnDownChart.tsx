import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// TokenBurnDownChart component
const TokenBurnDownChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the most recent execution
    fetch('/api/executions?limit=1')
      .then(res => res.json())
      .then(async executions => {
        if (executions && executions.length > 0) {
          const exec = executions[0];
          // Fetch details for the most recent execution
          const execRes = await fetch(`/api/executions/${exec.id}`);
          const execDetails = await execRes.json();
          // Transform step_results into chart data
          const stepResults = execDetails.step_results || {};
          const chartData = Object.entries(stepResults).map(([step, details]: any) => ({
            step,
            tokens: details.tokens || 0
          }));
          setData(chartData);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!data.length) return <div>No token data available.</div>;

  return (
    <div style={{ width: '100%', height: 250 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="tokens" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TokenBurnDownChart;
