import { create } from 'zustand';

export interface GraphData {
  nodes?: { name: string }[];
  edges?: { source: string; target: string }[];
}

interface RunState {
  output: string;
  progress: string[];
  loading: boolean;
  error: string;
  graph: GraphData | null;
  activeTask: string | null;
  tokenUsage: number;
  setLoading: (loading: boolean) => void;
  setError: (error: string) => void;
  addProgress: (msg: string) => void;
  setOutput: (output: string) => void;
  setGraph: (graph: GraphData | null) => void;
  setActiveTask: (task: string | null) => void;
  setTokenUsage: (usage: number) => void;
  reset: () => void;
}

export const useRunStore = create<RunState>(set => ({
  output: '',
  progress: [],
  loading: false,
  error: '',
  graph: null,
  activeTask: null,
  tokenUsage: 0,
  setLoading: loading => set({ loading }),
  setError: error => set({ error }),
  addProgress: msg => set(state => ({ progress: [...state.progress, msg] })),
  setOutput: output => set({ output }),
  setGraph: graph => set({ graph }),
  setActiveTask: task => set({ activeTask: task }),
  setTokenUsage: usage => set({ tokenUsage: usage }),
  reset: () =>
    set({
      output: '',
      progress: [],
      loading: false,
      error: '',
      graph: null,
      activeTask: null,
      tokenUsage: 0
    })
}));
