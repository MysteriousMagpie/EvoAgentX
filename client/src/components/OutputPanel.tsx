import type { FC } from 'react';

interface Props {
  output: string;
  progress: string[];
}
const OutputPanel: FC<Props> = ({ output, progress }) => {
  const text = [...progress, output].filter(Boolean).join('\n');
  return (
    <div className="mt-6 rounded-xl border p-4 bg-gray-50 whitespace-pre-line">
      {text || <span className="text-gray-400">No output yet.</span>}
    </div>
  );
};

export default OutputPanel;
