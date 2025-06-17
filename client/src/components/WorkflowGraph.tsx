import React from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import type { Node, Edge } from 'reactflow';
import { useRunStore } from '../store/useRunStore';
import 'reactflow/dist/style.css';

interface GraphData {
  nodes?: { name: string }[];
  edges?: { source: string; target: string }[];
}

export default function WorkflowGraph() {
  const { graph: data, activeTask: active } = useRunStore();
  const nodes: Node[] = (data?.nodes || []).map((n, idx) => ({
    id: n.name,
    data: { label: n.name },
    position: { x: 50, y: idx * 80 },
    className: active === n.name ? 'bg-green-200' : ''
  }));

  const edges: Edge[] = (data?.edges || []).map(e => ({
    id: `${e.source}-${e.target}`,
    source: e.source,
    target: e.target
  }));

  return (
    <div style={{ height: 400 }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
