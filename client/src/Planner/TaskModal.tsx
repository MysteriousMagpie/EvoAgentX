import React, { useState, useEffect } from 'react';

interface EventItem {
  id?: string;
  title?: string;
  start?: string;
  end?: string;
  notes?: string;
  tag?: string;
  priority?: 'Low' | 'Medium' | 'High';
  locked?: boolean;
  color?: string;
  recurrence?: string;
}

interface TaskModalProps {
  event: EventItem | null;
  onSave: (ev: Partial<EventItem>) => void;
  onDelete?: () => void;
  onClose: () => void;
  loading?: boolean;
}

const TAGS = ['focus', 'meeting', 'admin', 'rest'];
const PRIORITIES = ['Low', 'Medium', 'High'];
const RECURRENCES = ['None', 'Daily', 'Weekly', 'Custom'];

const TaskModal: React.FC<TaskModalProps> = ({ event, onSave, onDelete, onClose, loading }) => {
  const [title, setTitle] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [notes, setNotes] = useState('');
  const [tag, setTag] = useState('focus');
  const [priority, setPriority] = useState<'Low' | 'Medium' | 'High'>('Medium');
  const [locked, setLocked] = useState(false);
  const [color, setColor] = useState('#3b82f6');
  const [recurrence, setRecurrence] = useState('None');
  const [showToast, setShowToast] = useState(false);
  const [errors, setErrors] = useState<{ title?: string; start?: string; end?: string }>({});

  useEffect(() => {
    setTitle(event?.title || '');
    setStart(event?.start || '');
    setEnd(event?.end || '');
    setNotes(event?.notes || '');
    setTag(event?.tag || 'focus');
    setPriority(event?.priority || 'Medium');
    setLocked(event?.locked || false);
    setColor(event?.color || '#3b82f6');
    setRecurrence(event?.recurrence || 'None');
  }, [event]);

  const validate = () => {
    const newErrors: { title?: string; start?: string; end?: string } = {};
    if (!title.trim()) newErrors.title = 'Title is required.';
    if (!start) newErrors.start = 'Start time is required.';
    if (!end) newErrors.end = 'End time is required.';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSave({ title, start, end, notes, tag, priority, locked, color, recurrence });
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50 transition-opacity ease-in-out">
      <div className="bg-white dark:bg-gray-800 p-10 rounded-2xl shadow-2xl w-full max-w-lg relative transition-all duration-300 ease-in-out border border-gray-200 dark:border-gray-700">
        <button
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-xl focus:outline-none"
          onClick={onClose}
          aria-label="Close"
        >
          ✖️
        </button>
        <h4 className="font-bold text-2xl mb-6 flex items-center gap-2 border-b pb-3" style={{ color }}>
          {event ? 'Edit Event' : 'Add Event'}
        </h4>
        <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-1">
            <span className="font-medium mb-1">Title <span className="text-red-500">*</span></span>
            <input className={`p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition ${errors.title ? 'border-red-500' : ''}`} placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} required />
            {errors.title && <span className="text-xs text-red-500 mt-1">{errors.title}</span>}
          </label>
          <div className="flex gap-4">
            <label className="flex-1 flex flex-col gap-1">
              <span className="font-medium mb-1">Start Time <span className="text-red-500">*</span></span>
              <input type="datetime-local" className={`p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition ${errors.start ? 'border-red-500' : ''}`} value={start} onChange={e => setStart(e.target.value)} required />
              {errors.start && <span className="text-xs text-red-500 mt-1">{errors.start}</span>}
            </label>
            <label className="flex-1 flex flex-col gap-1">
              <span className="font-medium mb-1">End Time <span className="text-red-500">*</span></span>
              <input type="datetime-local" className={`p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition ${errors.end ? 'border-red-500' : ''}`} value={end} onChange={e => setEnd(e.target.value)} required />
              {errors.end && <span className="text-xs text-red-500 mt-1">{errors.end}</span>}
            </label>
          </div>
          <label className="flex flex-col gap-1">
            <span className="font-medium mb-1">Notes</span>
            <textarea className="p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition" placeholder="Notes" value={notes} onChange={e => setNotes(e.target.value)} />
          </label>
          <div className="flex gap-4">
            <label className="flex-1 flex flex-col gap-1">
              <span className="font-medium mb-1">Tag</span>
              <select className="p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition" value={tag} onChange={e => setTag(e.target.value)}>
                {TAGS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>
            <label className="flex-1 flex flex-col gap-1">
              <span className="font-medium mb-1">Priority</span>
              <select className="p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition" value={priority} onChange={e => setPriority(e.target.value as any)}>
                {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>
          </div>
          <div className="flex gap-4 items-center">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={locked} onChange={e => setLocked(e.target.checked)} className="accent-blue-600 w-5 h-5" />
              <span className="font-medium">Lock <span className="text-xs">(Don’t let EvoAgentX move this)</span></span>
            </label>
            <label className="flex items-center gap-2">
              <span className="font-medium">Color</span>
              <input type="color" value={color} onChange={e => setColor(e.target.value)} className="w-8 h-8 p-0 border-none bg-transparent rounded-full shadow" />
              <span className="inline-block w-6 h-6 rounded-full border ml-2" style={{ backgroundColor: color, borderColor: color }}></span>
            </label>
          </div>
          <label className="flex flex-col gap-1">
            <span className="font-medium mb-1">Recurrence</span>
            <select className="p-2 rounded border focus:outline-none focus:ring-2 focus:ring-blue-400 transition" value={recurrence} onChange={e => setRecurrence(e.target.value)}>
              {RECURRENCES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </label>
          <div className="flex gap-2 mt-2 justify-end border-t pt-4">
            {onDelete && (
              <button type="button" className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition" onClick={onDelete} disabled={loading}>{loading ? '...' : 'Delete'}</button>
            )}
            <button type="submit" className="bg-blue-600 text-white px-5 py-2 rounded-lg font-semibold shadow hover:bg-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-400" disabled={loading}>{loading ? 'Saving...' : 'Save'}</button>
            <button type="button" className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 transition" onClick={onClose} disabled={loading}>Cancel</button>
          </div>
        </form>
        {showToast && (
          <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-black text-white px-6 py-3 rounded shadow-lg text-lg animate-fade-in-out z-50">
            🤖 Schedule Updated
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskModal;
