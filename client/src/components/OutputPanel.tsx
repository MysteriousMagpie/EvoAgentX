import { FC } from 'react';

interface Props { output: string }
const OutputPanel: FC<Props> = ({ output }) => (
  <div className="mt-6 rounded-xl border p-4 bg-gray-50 whitespace-pre-line">
    {output || <span className="text-gray-400">No output yet.</span>}
  </div>
);

export default OutputPanel;
