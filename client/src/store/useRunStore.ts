import { create } from 'zustand';

export interface GraphData {
  nodes?: { name: string }[];
  edges?: { source: string; target: string }[];
}

export interface ProgressItem {
  message: string;
  timestamp: string;
  type?: string;
  state?: any;
  error?: any;
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
  saveRun: (run: RunRecord) => void;
  loadRuns: () => void;
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
  addProgress: msg => {
    let parsed;
    try {
      parsed = typeof msg === 'string' ? JSON.parse(msg) : msg;
    } catch {
      parsed = { message: msg };
    }
    set(state => ({
      progress: [
        ...state.progress,
        {
          message: parsed.message || msg,
          timestamp: new Date().toISOString(),
          type: parsed.type,
          state: parsed.state,
          error: parsed.error
        }
      ]
    }));
  },
  setOutput: output => set({ output }),
  setActiveTask: task => set({ activeTask: task }),
  setTokenUsage: usage => set({ tokenUsage: usage }),
  setRuns: runs => set({ runs }),
  addRun: run => set(state => ({ runs: [...state.runs, run] })),
  saveRun: run => {
    set(state => {
      const updated = [...state.runs, run];
      localStorage.setItem('runHistory', JSON.stringify(updated));
      return { runs: updated };
    });
  },
  loadRuns: () => {
    const data = localStorage.getItem('runHistory');
    if (data) set({ runs: JSON.parse(data) });
  },
  fetchRuns: async () => {
    // Disabled: /runs endpoint does not exist on backend
    // try {
    //   const res = await fetch('http://localhost:8000/runs');
    //   if (res.ok) {
    //     const data: RunRecord[] = await res.json();
    //     set({ runs: data });
    //   }
    // } catch (e) {
    //   console.error('Failed to fetch runs', e);
    // }
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
