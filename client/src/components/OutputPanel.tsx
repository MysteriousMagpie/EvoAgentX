import { useRunStore } from '../store/useRunStore';

export default function OutputPanel() {
  const { output, progress } = useRunStore();
  const text = [...progress, output].filter(Boolean).join('\n');
  return (
    <div className="mt-6 rounded-xl border p-4 bg-gray-50 whitespace-pre-line">
      {text || <span className="text-gray-400">No output yet.</span>}
    </div>
  );
}
