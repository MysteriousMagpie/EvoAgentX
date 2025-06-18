import React, { useState, useEffect } from 'react';

interface EventItem {
  id?: string;
  title?: string;
  start?: string;
  end?: string;
  notes?: string;
}

interface TaskModalProps {
  event: EventItem | null;
  onSave: (ev: Partial<EventItem>) => void;
  onDelete?: () => void;
  onClose: () => void;
  loading?: boolean;
}

// Placeholder for Task Modal
const TaskModal: React.FC<TaskModalProps> = ({ event, onSave, onDelete, onClose, loading }) => {
  const [title, setTitle] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    setTitle(event?.title || '');
    setStart(event?.start || '');
    setEnd(event?.end || '');
    setNotes(event?.notes || '');
  }, [event]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({ title, start, end, notes });
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div className="bg-white dark:bg-gray-800 p-6 rounded shadow-lg w-96">
        <h4 className="font-bold mb-2">{event ? 'Edit Event' : 'Add Event'}</h4>
        <form className="flex flex-col gap-2" onSubmit={handleSubmit}>
          <input className="p-2 rounded border" placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} required />
          <input className="p-2 rounded border" placeholder="Start (ISO)" value={start} onChange={e => setStart(e.target.value)} required />
          <input className="p-2 rounded border" placeholder="End (ISO)" value={end} onChange={e => setEnd(e.target.value)} required />
          <textarea className="p-2 rounded border" placeholder="Notes" value={notes} onChange={e => setNotes(e.target.value)} />
          <div className="flex gap-2 mt-2">
            <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded" disabled={loading}>{loading ? 'Saving...' : 'Save'}</button>
            {onDelete && (
              <button type="button" className="bg-red-500 text-white px-3 py-1 rounded" onClick={onDelete} disabled={loading}>{loading ? '...' : 'Delete'}</button>
            )}
            <button type="button" className="bg-gray-300 px-3 py-1 rounded" onClick={onClose} disabled={loading}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskModal;
