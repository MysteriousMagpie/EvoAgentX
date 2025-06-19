import React, { useState } from "react";
import AppLayout from "./AppLayout";

interface Event {
  title: string;
  start: string;
  end: string;
  notes?: string;
  locked?: boolean;
}

interface EventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (event: Event) => void;
}

function EventModal({ isOpen, onClose, onSave }: EventModalProps) {
  const [title, setTitle] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [notes, setNotes] = useState("");
  const [locked, setLocked] = useState(false);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-gray-800 p-6 rounded shadow w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Add New Event</h2>
        <input
          className="w-full mb-2 p-2 border rounded"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <div className="flex gap-2 mb-2">
          <input
            type="time"
            className="w-1/2 p-2 border rounded"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
          <input
            type="time"
            className="w-1/2 p-2 border rounded"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </div>
        <textarea
          className="w-full mb-2 p-2 border rounded"
          placeholder="Notes (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <div className="mb-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={locked}
              onChange={(e) => setLocked(e.target.checked)}
            />
            <span>Lock this event (AI can't move it)</span>
          </label>
        </div>
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 border rounded">
            Cancel
          </button>
          <button
            onClick={() => {
              onSave({ title, start, end, notes, locked });
              onClose();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Planner() {
  const [showModal, setShowModal] = useState(false);
  const [events, setEvents] = useState<Event[]>([
    { title: "Write EvoAgentX Update", start: "09:00", end: "10:00" },
    { title: "Deep Work Session: Calendar Sync", start: "11:00", end: "12:00" },
  ]);

  return (
    <AppLayout>
      <EventModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSave={(event) => setEvents([...events, event])}
      />

      <div className="flex flex-col md:flex-row gap-4 h-full">
        <section className="flex-1 bg-white dark:bg-gray-800 p-4 rounded shadow overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-semibold">Today</h1>
            <button className="text-sm px-4 py-1 border rounded">Jump to Date</button>
          </div>

          <div className="space-y-4">
            {events.map((event, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-2">
                <div className="text-sm text-gray-500">
                  {event.start} - {event.end}
                </div>
                <div className="font-medium">{event.title}</div>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <button
              onClick={() => setShowModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Add Event
            </button>
          </div>
        </section>

        <aside className="w-full md:w-1/3 bg-gray-50 dark:bg-gray-900 p-4 rounded shadow h-full">
          <h2 className="text-xl font-medium mb-2">Suggested Tasks (AI Zone)</h2>
          <ul className="space-y-4">
            <li className="p-3 bg-white dark:bg-gray-700 rounded shadow">
              <div className="font-medium">Review feedback notes</div>
              <div className="text-sm text-gray-500 mb-2">Priority: Medium</div>
              <div className="flex gap-2">
                <button className="text-sm px-3 py-1 bg-green-600 text-white rounded">Add to Plan</button>
                <button className="text-sm px-3 py-1 border rounded">Refine</button>
              </div>
            </li>
            <li className="text-gray-500 italic">No suggestions yet.</li>
          </ul>
        </aside>
      </div>
    </AppLayout>
  );
}
