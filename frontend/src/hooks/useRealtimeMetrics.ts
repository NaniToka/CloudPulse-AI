/**
 * Custom React Hook for Real-Time Metric WebSockets & 300-Point Sliding Window Buffer.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import type { MetricPoint, TelemetryWebSocketMessage } from "@/types/metric";
import { metricService } from "@/services/metricService";

const WS_URL =
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
  window.location.host +
  "/api/v1/metrics/ws";

export function useRealtimeMetrics() {
  const [current, setCurrent] = useState<MetricPoint | null>(null);
  const [history, setHistory] = useState<MetricPoint[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [lastAlert, setLastAlert] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initial History Seed
  useEffect(() => {
    metricService.getHistory(300).then((res) => {
      if (res && res.history && res.history.length > 0) {
        setHistory(res.history);
        setCurrent(res.history[res.history.length - 1]);
      }
    }).catch(() => {});
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const socket = new WebSocket(WS_URL);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        if (isPaused) return;

        try {
          const message: TelemetryWebSocketMessage = JSON.parse(event.data);
          if (message.event === "telemetry_update" && message.data) {
            const newPoint = message.data;

            // Trigger real-time alert toast if CPU > 88%
            if (newPoint.cpu_usage > 88.0) {
              setLastAlert(`High CPU Spike Detected: ${newPoint.cpu_usage.toFixed(1)}%`);
            }

            setCurrent(newPoint);

            // Maintain sliding window buffer of max 300 points
            setHistory((prev) => {
              const updated = [...prev, newPoint];
              return updated.length > 300 ? updated.slice(updated.length - 300) : updated;
            });
          }
        } catch (e) {
          // Ignore heartbeat or parse errors
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => connect(), 3000);
      };

      socket.onerror = () => {
        socket.close();
      };
    } catch (e) {
      reconnectTimeoutRef.current = setTimeout(() => connect(), 3000);
    }
  }, [isPaused]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  const togglePause = useCallback(() => {
    setIsPaused((prev) => !prev);
  }, []);

  const clearAlert = useCallback(() => {
    setLastAlert(null);
  }, []);

  return {
    current,
    history,
    isConnected,
    isPaused,
    togglePause,
    lastAlert,
    clearAlert,
  };
}
