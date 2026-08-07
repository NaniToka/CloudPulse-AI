import React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Terminal } from "lucide-react";
import { TelemetryEventItem } from "@/services/telemetryService";
import { format } from "date-fns";

interface LogViewerProps {
  events: TelemetryEventItem[];
}

export const LogViewer: React.FC<LogViewerProps> = ({ events }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return "bg-red-500 hover:bg-red-600";
      case "ERROR":
        return "bg-orange-500 hover:bg-orange-600";
      case "WARN":
        return "bg-yellow-500 hover:bg-yellow-600";
      case "INFO":
        return "bg-blue-500 hover:bg-blue-600";
      default:
        return "bg-gray-500 hover:bg-gray-600";
    }
  };

  return (
    <Card className="col-span-2 md:col-span-1 border border-border/50">
      <CardHeader className="bg-muted/30 py-3 border-b">
        <CardTitle className="text-sm font-semibold flex items-center">
          <Terminal className="w-4 h-4 mr-2" />
          Live Log Stream
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="h-[400px] overflow-y-auto bg-slate-950 p-4 font-mono text-xs">
          {events.length === 0 ? (
            <div className="text-slate-500 text-center mt-10">Waiting for logs...</div>
          ) : (
            <div className="space-y-2 flex flex-col-reverse">
              {events.map((event) => (
                <div key={event.id} className="flex gap-3 py-1 border-b border-slate-800/50 hover:bg-slate-900/50 rounded px-1 transition-colors">
                  <span className="text-slate-500 whitespace-nowrap">
                    {format(new Date(event.timestamp), "HH:mm:ss.SSS")}
                  </span>
                  <Badge className={`text-[10px] h-4 px-1 rounded-sm ${getSeverityColor(event.severity)}`}>
                    {event.severity}
                  </Badge>
                  <span className="text-slate-400 whitespace-nowrap min-w-[80px]">[{event.source}]</span>
                  <span className="text-slate-300 break-all">
                    {event.raw_payload?.message || "Event recorded"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
