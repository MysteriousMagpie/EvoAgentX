import { create } from 'zustand';

export interface GraphData {
  nodes?: { name: string }[];
  edges?: { source: string; target: string }[];
}

export interface ProgressItem {
  message: string;
  timestamp: string;
}

export interface RunRecord {
  id: number;
  goal: string;
  status: '✅' | '❌';
  tokens: number;
  cost: number;
  time: string;
}

interface RunState {
  output: string;
  progress: ProgressItem[];
  loading: boolean;
  error: string;
  activeTask: string | null;
  tokenUsage: number;
  runs: RunRecord[];
  setLoading: (loading: boolean) => void;
  setError: (error: string) => void;
  addProgress: (msg: string) => void;
  setRuns: (runs: RunRecord[]) => void;
  addRun: (run: RunRecord) => void;
  fetchRuns: () => Promise<void>;
  setOutput: (output: string) => void;
  setActiveTask: (task: string | null) => void;
  setTokenUsage: (usage: number) => void;
  reset: () => void;
}

export const useRunStore = create<RunState>(set => ({
  output: '',
  progress: [],
  loading: false,
  error: '',
  activeTask: null,
  tokenUsage: 0,
  runs: [],
  setLoading: loading => set({ loading }),
  setError: error => set({ error }),
  addProgress: msg => set(state => ({ progress: [...state.progress, { message: msg, timestamp: new Date().toISOString() }] })),
  setOutput: output => set({ output }),
  setActiveTask: task => set({ activeTask: task }),
  setTokenUsage: usage => set({ tokenUsage: usage }),
  setRuns: runs => set({ runs }),
  addRun: run => set(state => ({ runs: [...state.runs, run] })),
  fetchRuns: async () => {
    try {
      const res = await fetch('http://localhost:8000/runs');
      if (res.ok) {
        const data: RunRecord[] = await res.json();
        set({ runs: data });
      }
    } catch (e) {
      console.error('Failed to fetch runs', e);
    }
  },
  reset: () =>
    set({
      output: '',
      progress: [],
      loading: false,
      error: '',
      activeTask: null,
      tokenUsage: 0,
      runs: []
    })
}));
