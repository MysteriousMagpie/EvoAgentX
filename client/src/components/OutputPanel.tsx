import { useRunStore } from '../store/useRunStore';
import ReactMarkdown from 'react-markdown';
import { useEffect, useRef, useState } from 'react';

function formatTime(iso: string) {
  const date = new Date(iso);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function OutputPanel() {
  const { output, progress } = useRunStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const [highlightedIdx, setHighlightedIdx] = useState<number | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [progress, output]);

  useEffect(() => {
    if (progress.length > 0) {
      setHighlightedIdx(progress.length - 1);
      const timer = setTimeout(() => setHighlightedIdx(null), 1200);
      return () => clearTimeout(timer);
    }
  }, [progress]);

  return (
    <div
      ref={containerRef}
      className="mt-6 rounded-xl border p-4 bg-gray-50"
      style={{ maxHeight: 400, overflowY: 'auto' }}
    >
      {progress.length > 0 ? (
        progress.map((item, idx) => (
          <div
            key={idx}
            className={`mb-2 flex items-start gap-2 transition-colors duration-500 ${highlightedIdx === idx ? 'bg-yellow-100' : ''}`}
          >
            <span className="text-xs text-gray-400 min-w-[70px]">[{formatTime(item.timestamp)}]</span>
            <span className="flex-1"><ReactMarkdown>{item.message}</ReactMarkdown></span>
          </div>
        ))
      ) : (
        <span className="text-gray-400">No output yet.</span>
      )}
      {output && (
        <div className="mt-2">
          <ReactMarkdown>{output}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
