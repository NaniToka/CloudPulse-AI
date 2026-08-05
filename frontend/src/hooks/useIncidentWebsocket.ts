/**
 * React hook for real-time WebSockets in Incident Management Center
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/useToast";
import type { IncidentWebSocketEvent } from "@/types/incident";

export function useIncidentWebsocket(onEventReceived?: (event: IncidentWebSocketEvent) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const connect = useCallback(() => {
    // Build WebSocket URL from location or env
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = import.meta.env.VITE_WS_HOST || window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/incidents/ws`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt reconnect after 5 seconds
        setTimeout(() => connect(), 5000);
      };

      ws.onerror = (err) => {
        console.warn("Incident WebSocket error:", err);
        setIsConnected(false);
      };

      ws.onmessage = (eventMessage) => {
        try {
          const payload: IncidentWebSocketEvent = JSON.parse(eventMessage.data);
          
          // Invalidate React Query caches
          queryClient.invalidateQueries({ queryKey: ["incidents"] });
          queryClient.invalidateQueries({ queryKey: ["incident-analytics"] });

          // Fire optional callback
          if (onEventReceived) {
            onEventReceived(payload);
          }

          // Trigger toasts
          if (payload.event === "incident_created" && payload.data) {
            toast({
              title: `🔥 New Incident: [${payload.data.severity}] ${payload.data.title}`,
              description: `Service: ${payload.data.affected_service} | Status: ${payload.data.status}`,
              variant: payload.data.severity === "P0" || payload.data.severity === "P1" ? "destructive" : "default",
            });
          } else if (payload.event === "incident_resolved" && payload.data) {
            toast({
              title: `✅ Incident Resolved: ${payload.data.title}`,
              description: payload.resolution_notes || "Resolution details logged.",
            });
          } else if (payload.event === "severity_changed") {
            toast({
              title: `⚠️ Severity Changed: ${payload.old_severity} ➔ ${payload.new_severity}`,
              description: payload.data?.title,
            });
          } else if (payload.event === "assignment_changed") {
            toast({
              title: `👤 Engineer Reassigned: ${payload.new_engineer || "Unassigned"}`,
              description: payload.data?.title,
            });
          }
        } catch (e) {
          console.warn("Error parsing WebSocket event payload", e);
        }
      };
    } catch (e) {
      console.warn("Failed to instantiate WebSocket:", e);
    }
  }, [queryClient, toast, onEventReceived]);

  useEffect(() => {
    connect();

    // Ping interval to keep connection alive
    const pingInterval = setInterval(() => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send("ping");
      }
    }, 25000);

    return () => {
      clearInterval(pingInterval);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected };
}
