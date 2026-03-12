"use client";

import { useEffect } from "react";
import { io } from "socket.io-client";

export function useWebSocket() {
  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_SOCKET_URL || "http://localhost:8000");
    return () => {
      socket.disconnect();
    };
  }, []);
}
