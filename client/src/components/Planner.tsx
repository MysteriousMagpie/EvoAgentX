import { useState } from 'react';
import TaskModal from '../Planner/TaskModal';

export interface EventItem {
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

export default function Planner() {
  const [showModal, setShowModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSave = (event: Partial<EventItem>) => {
    setLoading(true);
    setTimeout(() => {
      if (selectedEvent) {
        setEvents(evts => evts.map(e => e.id === selectedEvent.id ? { ...e, ...event } : e));
      } else {
        setEvents(evts => [...evts, { ...event, id: Date.now().toString() }]);
      }
      setShowModal(false);
      setSelectedEvent(null);
      setLoading(false);
    }, 800);
  };

  const handleDelete = () => {
    if (selectedEvent) {
      setEvents(evts => evts.filter(e => e.id !== selectedEvent.id));
      setShowModal(false);
      setSelectedEvent(null);
    }
  };

  const openModal = (event?: EventItem) => {
    setSelectedEvent(event || null);
    setShowModal(true);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <button
        className="px-6 py-3 bg-primary text-white rounded-lg shadow hover:bg-primary-dark transition"
        onClick={() => openModal()}
      >
        Add Event
      </button>
      <div className="w-full max-w-2xl mt-8">
        {events.length === 0 ? (
          <div className="text-center text-gray-400">No events yet. Add your first event!</div>
        ) : (
          <ul className="space-y-4">
            {events.map(event => (
              <li key={event.id} className="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg shadow p-4 border-l-8" style={{ borderColor: event.color || '#3b82f6' }}>
                <div>
                  <div className="font-bold text-lg flex items-center gap-2">
                    {event.title} {event.locked && <span title="Locked" className="text-xs">🔒</span>}
                  </div>
                  <div className="text-sm text-gray-500">{event.start} - {event.end}</div>
                  <div className="text-xs mt-1"><span className="px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 mr-2">{event.tag}</span> <span className="font-semibold">{event.priority}</span></div>
                  {event.notes && <div className="text-xs mt-1 text-gray-400">{event.notes}</div>}
                </div>
                <button className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition" onClick={() => openModal(event)}>Edit</button>
              </li>
            ))}
          </ul>
        )}
      </div>
      {showModal && (
        <TaskModal
          event={selectedEvent}
          onSave={handleSave}
          onDelete={selectedEvent ? handleDelete : undefined}
          onClose={() => { setShowModal(false); setSelectedEvent(null); }}
          loading={loading}
        />
      )}
    </div>
  );
}
