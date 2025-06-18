import { useEffect } from 'react';

interface ToastProps {
  message: string;
  onClose: () => void;
  duration?: number;
}

export default function Toast({ message, onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [message, onClose, duration]);

  if (!message) return null;

  return (
    <div className="fixed top-6 right-6 z-50 bg-red-600 text-white px-4 py-2 rounded shadow-lg animate-fade-in">
      {message}
    </div>
  );
}
