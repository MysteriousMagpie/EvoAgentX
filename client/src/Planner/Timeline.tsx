import React, { useEffect, useState } from 'react';
import TaskModal from './TaskModal';
import { API_URL } from '../api';

interface EventItem {
  id: string;
  title: string;
  start: string;
  end: string;
  notes?: string;
}

const Timeline: React.FC = () => {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/events`);
      if (!res.ok) throw new Error('Failed to load events');
      const data = await res.json();
      setEvents(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadEvents(); }, []);

  const handleAdd = () => {
    setEditing(null);
    setModalOpen(true);
  };
  const handleEdit = (ev: EventItem) => {
    setEditing(ev);
    setModalOpen(true);
  };
  const handleClose = () => {
    setModalOpen(false);
    setEditing(null);
  };
  const handleSave = async (ev: Partial<EventItem>) => {
    setLoading(true);
    setError(null);
    try {
      if (editing) {
        await fetch(`${API_URL}/events/${editing.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(ev),
        });
      } else {
        await fetch(`${API_URL}/events`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(ev),
        });
      }
      await loadEvents();
      handleClose();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  const handleDelete = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await fetch(`${API_URL}/events/${id}`, { method: 'DELETE' });
      await loadEvents();
      handleClose();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="flex-1 p-4 overflow-y-auto bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700">
      <div className="flex justify-between items-center mb-4">
        <span className="font-bold text-lg">Events</span>
        <button className="bg-blue-600 text-white px-3 py-1 rounded" onClick={handleAdd}>Add Event</button>
      </div>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      <ul className="space-y-2">
        {events.map(ev => (
          <li key={ev.id} className="bg-white dark:bg-gray-800 p-3 rounded shadow flex justify-between items-center">
            <div>
              <div className="font-semibold">{ev.title}</div>
              <div className="text-xs text-gray-500">{ev.start} - {ev.end}</div>
              {ev.notes && <div className="text-xs text-gray-400">{ev.notes}</div>}
            </div>
            <button className="text-blue-600 text-sm" onClick={() => handleEdit(ev)}>Edit</button>
          </li>
        ))}
      </ul>
      {modalOpen && (
        <TaskModal
          event={editing}
          onSave={handleSave}
          onDelete={editing ? () => handleDelete(editing.id) : undefined}
          onClose={handleClose}
          loading={loading}
        />
      )}
    </section>
  );
};

export default Timeline;
