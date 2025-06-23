import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MetricsChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        console.log('Fetching:', '/api/executions?limit=1');
        const res = await fetch('/api/executions?limit=1');
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const executions = await res.json();
        if (executions && executions.length > 0) {
          const exec = executions[0];
          const results = exec.results || {};
          const chartData = Object.entries(results)
            .filter(([_, v]) => typeof v === 'number')
            .map(([metric, value]) => ({ metric, value }));
          setData(chartData);
        }
      } catch (err) {
        console.error('Failed to fetch metrics', err);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!data.length) return <div>No metrics available.</div>;

  return (
    <div style={{ width: '100%', height: 250 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;
