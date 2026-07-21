import { useState, useEffect } from 'react';
import { StreamEvent } from '../lib/types';

export function useSSE(url: string | null) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!url) return;

    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const parsedEvent: StreamEvent = JSON.parse(event.data);
        setEvents((prev) => [...prev, parsedEvent]);
      } catch (e) {
        console.error('Failed to parse SSE message', e);
      }
    };

    eventSource.onerror = (e) => {
      console.error('SSE Error:', e);
      setError(new Error('SSE Connection Error'));
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [url]);

  return { events, isConnected, error };
}
