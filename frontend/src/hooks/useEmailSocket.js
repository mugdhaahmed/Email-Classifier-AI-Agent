import { useState, useEffect } from 'react';

export const useEmailSocket = () => {
  const [notifications, setNotifications] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // 1. Fetch past stored alerts from our Django REST Framework view endpoint upon mounting
    fetch('http://127.0.0.1:8000/api/notifications/')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setNotifications(data);
        }
      })
      .catch((err) => console.error("[REST SYNC ERROR] Failed hydration sync:", err));

    // 2. Open up a persistent live channel pipeline to our Daphne server instance
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/emails/');

    socket.onopen = () => {
      setIsConnected(true);
      console.log("[WEBSOCKET CONNECTED] Real-time stream is live.");
    };

    socket.onmessage = (event) => {
      const incomingAlert = JSON.parse(event.data);
      
      setNotifications((prev) => {
        // Enforce strict prevention to ensure unique rendering keys across lists
        if (prev.some((item) => item.email_id === incomingAlert.email_id)) {
          return prev;
        }
        return [incomingAlert, ...prev];
      });
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log("[WEBSOCKET DISCONNECTED] Stream closed.");
    };

    socket.onerror = (error) => {
      console.error("[WEBSOCKET ERROR] Network exception observed:", error);
    };

    // Clean up connections gracefully on interface unmount
    return () => {
      socket.close();
    };
  }, []);

  return { notifications, isConnected };
};