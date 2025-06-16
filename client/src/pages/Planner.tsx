import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

interface EventItem {
  id: number;
  title: string;
  start: string;
  end: string;
}

export default function Planner() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [title, setTitle] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [editing, setEditing] = useState<EventItem | null>(null);

  const loadEvents = async () => {
    const res = await fetch('http://localhost:8000/events');
    if (res.ok) {
      const data = await res.json();
      setEvents(data);
    }
  };

  useEffect(() => { void loadEvents(); }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = { title, start, end };
    if (editing) {
      await fetch(`http://localhost:8000/events/${editing.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      await fetch('http://localhost:8000/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }
    setTitle('');
    setStart('');
    setEnd('');
    setEditing(null);
    void loadEvents();
  };

  const edit = (ev: EventItem) => {
    setEditing(ev);
    setTitle(ev.title);
    setStart(ev.start);
    setEnd(ev.end);
  };

  const remove = async (id: number) => {
    await fetch(`http://localhost:8000/events/${id}`, { method: 'DELETE' });
    void loadEvents();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Today's Events</h2>
      <form onSubmit={submit} className="space-x-2">
        <input
          className="border p-1 rounded"
          placeholder="Title"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />
        <input
          className="border p-1 rounded"
          placeholder="Start"
          value={start}
          onChange={e => setStart(e.target.value)}
        />
        <input
          className="border p-1 rounded"
          placeholder="End"
          value={end}
          onChange={e => setEnd(e.target.value)}
        />
        <button className="px-2 py-1 bg-blue-600 text-white rounded" type="submit">
          {editing ? 'Update' : 'Add'}
        </button>
      </form>
      <ul className="space-y-1">
        {events.map(ev => (
          <li key={ev.id} className="flex items-center space-x-2">
            <span className="flex-1">
              {ev.title} {ev.start} - {ev.end}
            </span>
            <button className="text-sm text-blue-600" onClick={() => edit(ev)}>Edit</button>
            <button className="text-sm text-red-600" onClick={() => remove(ev.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
